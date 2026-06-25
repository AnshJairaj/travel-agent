"""
Trip Planner Agent (Orchestrator) — the brain of the whole system.
It takes the user's natural language request, extracts trip details,
runs Flight/Train/Hotel/Cab agents IN PARALLEL using asyncio,
then hands results to the Approval Agent.
"""

import asyncio
from agents.base_agent import BaseAgent
from agents.flight_agent import FlightAgent
from agents.train_agent import TrainAgent
from agents.hotel_agent import HotelAgent
from agents.cab_agent import CabAgent
from agents.approval_agent import ApprovalAgent


class TripPlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Trip Planner Agent",
            system_prompt=(
                "You extract structured trip details from a user's natural language request. "
                "Return ONLY a JSON object with keys: origin_city, destination_city, "
                "departure_date (YYYY-MM-DD), return_date (YYYY-MM-DD or null), "
                "hotel_checkin (YYYY-MM-DD), hotel_checkout (YYYY-MM-DD). "
                "If the user doesn't give exact dates, pick a reasonable date 14 days from today."
            ),
        )
        self.flight_agent = FlightAgent()
        self.train_agent = TrainAgent()
        self.hotel_agent = HotelAgent()
        self.cab_agent = CabAgent()
        self.approval_agent = ApprovalAgent()

    def extract_trip_details(self, user_request: str) -> dict:
        self.log("Understanding user request...")
        return self.ask_gpt_json(user_request)

    async def run_parallel_search(self, details: dict):
        """
        Runs Flight, Train, Hotel, and Cab searches AT THE SAME TIME
        instead of one after another - this is the 'parallel agents' part
        from your diagram.
        """
        loop = asyncio.get_event_loop()

        origin = details["origin_city"]
        destination = details["destination_city"]
        dep_date = details["departure_date"]
        checkin = details.get("hotel_checkin", dep_date)
        checkout = details.get("hotel_checkout", dep_date)

        # Each .run_in_executor wraps a blocking call so they all run concurrently
        flight_task = loop.run_in_executor(
            None, self.flight_agent.search, origin, destination, dep_date
        )
        train_task = loop.run_in_executor(
            None, self.train_agent.search, origin, destination, dep_date
        )
        hotel_task = loop.run_in_executor(
            None, self.hotel_agent.search, destination, checkin, checkout
        )
        cab_task = loop.run_in_executor(
            None,
            self.cab_agent.estimate,
            f"{destination} Airport",
            f"{destination} City Center",
        )

        flight_result, train_result, hotel_result, cab_result = await asyncio.gather(
            flight_task, train_task, hotel_task, cab_task
        )

        return {
            "flight": flight_result,
            "train": train_result,
            "hotel": hotel_result,
            "cab": cab_result,
        }

    def pick_cheaper_travel_option(self, flight: dict, train: dict) -> dict:
        """Compares flight vs train price and returns the cheaper one."""
        flight_price = flight.get("price") if "error" not in flight else None
        train_price = train.get("price") if "error" not in train else None

        if flight_price is None and train_price is None:
            return {"error": "No travel option found"}
        if flight_price is None:
            return train
        if train_price is None:
            return flight

        return flight if float(flight_price) <= float(train_price) else train

    async def plan_trip(self, user_request: str) -> dict:
        """
        Main entry point - call this from the Streamlit app.
        Returns a dict with everything needed to show the user.
        """
        details = self.extract_trip_details(user_request)
        self.log(f"Extracted details: {details}")

        search_results = await self.run_parallel_search(details)

        best_travel = self.pick_cheaper_travel_option(
            search_results["flight"], search_results["train"]
        )

        summary = self.approval_agent.build_summary(
            best_travel, search_results["hotel"], search_results["cab"]
        )
        total_cost = self.approval_agent.calculate_total(
            best_travel, search_results["hotel"], search_results["cab"]
        )

        return {
            "details": details,
            "flight": search_results["flight"],
            "train": search_results["train"],
            "best_travel_option": best_travel,
            "hotel": search_results["hotel"],
            "cab": search_results["cab"],
            "summary": summary,
            "total_cost": total_cost,
        }


if __name__ == "__main__":
    planner = TripPlannerAgent()
    result = asyncio.run(
        planner.plan_trip(
            "Book my trip from Kolkata to Mumbai, cheapest direct flight or train, "
            "3-star hotel, with cab from airport to hotel."
        )
    )
    print(result)
