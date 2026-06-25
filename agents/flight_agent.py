"""
Flight Agent — uses Aviationstack API (free, no approval needed) to get real flight data,
then GPT picks/formats the best option.

Note: Aviationstack free tier gives flight schedules (not live pricing), so we combine
real flight/airline data with a realistic GPT-estimated price for the demo.
"""

import os
import httpx
from dotenv import load_dotenv
from agents.base_agent import BaseAgent

load_dotenv()

CITY_TO_IATA = {
    "kolkata": "CCU",
    "mumbai": "BOM",
    "delhi": "DEL",
    "bangalore": "BLR",
    "chennai": "MAA",
    "hyderabad": "HYD",
    "pune": "PNQ",
}


class FlightAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Flight Search Agent",
            system_prompt=(
                "You are a flight search assistant. Given real flight schedule data (airline, "
                "flight number, departure/arrival times) for a route, pick the most convenient "
                "direct flight and estimate a realistic INR price for that route based on typical "
                "Indian domestic airfares. Return ONLY a JSON object with keys: "
                "airline, flight_number, price, currency, departure_time, arrival_time, "
                "duration, is_direct."
            ),
        )
        self.api_key = os.getenv("AVIATIONSTACK_API_KEY")

    def search(self, origin_city: str, destination_city: str, date: str) -> dict:
        origin_code = CITY_TO_IATA.get(origin_city.lower())
        dest_code = CITY_TO_IATA.get(destination_city.lower())

        if not origin_code or not dest_code:
            return {"error": f"Unknown airport code for {origin_city} or {destination_city}"}

        self.log(f"Searching flights {origin_code} -> {dest_code}")

        url = "http://api.aviationstack.com/v1/flights"
        params = {
            "access_key": self.api_key,
            "dep_iata": origin_code,
            "arr_iata": dest_code,
            "limit": 5,
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as e:
            self.log(f"Aviationstack error: {e}")
            return {"error": str(e)}

        flights = data.get("data", [])
        if not flights:
            return {"error": f"No scheduled flights found for {origin_code}-{dest_code} route"}

        result = self.ask_gpt_json(
            f"Real flight data for {origin_city} to {destination_city} on {date}: "
            f"{flights[:5]}. Pick the best direct option and estimate price."
        )
        return result


if __name__ == "__main__":
    agent = FlightAgent()
    result = agent.search("Kolkata", "Mumbai", "2026-07-15")
    print(result)
