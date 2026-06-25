"""
Approval Agent — takes results from all search agents and formats them
into a single, clean itinerary summary for the user to approve.
"""

from agents.base_agent import BaseAgent


class ApprovalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Approval Agent",
            system_prompt=(
                "You are a travel itinerary formatter. Given flight/train, hotel, and cab "
                "details in JSON, combine them into a clean, friendly summary the user can "
                "read in 10 seconds. Include a clear TOTAL COST line at the end."
            ),
        )

    def build_summary(
        self, travel_option: dict, hotel: dict, cab: dict
    ) -> str:
        self.log("Building itinerary summary for user approval")

        combined_input = (
            f"Travel option: {travel_option}\n"
            f"Hotel: {hotel}\n"
            f"Cab: {cab}\n\n"
            "Format this into a readable itinerary with a TOTAL COST line."
        )
        summary = self.ask_gpt(combined_input)
        return summary

    def calculate_total(self, travel_option: dict, hotel: dict, cab: dict) -> float:
        """Adds up the numeric costs - simple Python math, no AI needed here."""
        total = 0.0
        total += float(travel_option.get("price", 0) or 0)
        total += float(hotel.get("price_per_night", 0) or 0)
        total += float(cab.get("estimated_fare_max", 0) or 0)
        return round(total, 2)
