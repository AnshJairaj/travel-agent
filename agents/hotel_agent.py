"""
Hotel Agent — Amadeus hotel search shut down its free signup, so this uses a realistic
mock hotel dataset per city instead. GPT still does the "picking the best option" reasoning,
which is the actual AI agent behavior you want to demonstrate.

To upgrade later: replace MOCK_HOTELS with a real API like Booking.com Affiliate API
(requires approval) or RapidAPI's "Hotels" listings.
"""

from agents.base_agent import BaseAgent

MOCK_HOTELS = {
    "mumbai": [
        {"hotel_name": "Hotel Suba International", "rating": 3, "price_per_night": 2800, "address": "Andheri East, Mumbai"},
        {"hotel_name": "The Fern Residency", "rating": 3, "price_per_night": 3200, "address": "Powai, Mumbai"},
        {"hotel_name": "Ramee Guestline", "rating": 3, "price_per_night": 2600, "address": "Juhu, Mumbai"},
    ],
    "delhi": [
        {"hotel_name": "Hotel City Star", "rating": 3, "price_per_night": 2200, "address": "Paharganj, Delhi"},
        {"hotel_name": "The Pearl Hotel", "rating": 3, "price_per_night": 2900, "address": "Karol Bagh, Delhi"},
    ],
    "kolkata": [
        {"hotel_name": "Hotel Hindusthan International", "rating": 3, "price_per_night": 2500, "address": "Park Street, Kolkata"},
        {"hotel_name": "The Sonnet Kolkata", "rating": 3, "price_per_night": 2700, "address": "Salt Lake, Kolkata"},
    ],
    "bangalore": [
        {"hotel_name": "Treebo Trend", "rating": 3, "price_per_night": 2400, "address": "MG Road, Bangalore"},
        {"hotel_name": "Hotel Royal Orchid Central", "rating": 3, "price_per_night": 3100, "address": "Manipal Centre, Bangalore"},
    ],
    "chennai": [
        {"hotel_name": "Hotel Palmgrove", "rating": 3, "price_per_night": 2300, "address": "T Nagar, Chennai"},
    ],
    "hyderabad": [
        {"hotel_name": "Hotel Marigold", "rating": 3, "price_per_night": 2400, "address": "Banjara Hills, Hyderabad"},
    ],
    "pune": [
        {"hotel_name": "Hotel Sunderban", "rating": 3, "price_per_night": 2300, "address": "Camp, Pune"},
    ],
}


class HotelAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Hotel Search Agent",
            system_prompt=(
                "You are a hotel search assistant. Given a list of 3-star hotels with prices, "
                "pick the best value option (good price relative to rating). Return ONLY a "
                "JSON object with keys: hotel_name, rating, price_per_night, currency, address."
            ),
        )

    def search(self, city: str, check_in: str, check_out: str) -> dict:
        self.log(f"Searching hotels in {city} ({check_in} to {check_out})")

        hotels = MOCK_HOTELS.get(city.lower())
        if not hotels:
            return {"error": f"No hotel data available for {city}"}

        result = self.ask_gpt_json(
            f"Here are available 3-star hotels in {city}: {hotels}. Pick the best value one."
        )
        result["currency"] = "INR"
        return result


if __name__ == "__main__":
    agent = HotelAgent()
    result = agent.search("Mumbai", "2026-07-15", "2026-07-17")
    print(result)
