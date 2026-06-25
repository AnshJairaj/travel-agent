"""
Cab Agent — uses OpenRouteService (free, no credit card required) to estimate
distance/time from airport/station to hotel, then GPT estimates a fare range.

Sign up free at: https://openrouteservice.org/dev/#/signup
"""

import os
import httpx
from dotenv import load_dotenv
from agents.base_agent import BaseAgent

load_dotenv()

# A few common Indian city landmark coordinates (lon, lat) for the demo.
# OpenRouteService needs coordinates, not addresses, on the free tier.
CITY_COORDS = {
    "mumbai": {"airport": [72.8656, 19.0896], "city_center": [72.8311, 18.9750]},
    "delhi": {"airport": [77.1025, 28.5562], "city_center": [77.2090, 28.6139]},
    "kolkata": {"airport": [88.4467, 22.6547], "city_center": [88.3639, 22.5726]},
    "bangalore": {"airport": [77.7066, 13.1986], "city_center": [77.5946, 12.9716]},
    "chennai": {"airport": [80.1709, 12.9941], "city_center": [80.2707, 13.0827]},
    "hyderabad": {"airport": [78.4294, 17.2403], "city_center": [78.4867, 17.3850]},
    "pune": {"airport": [73.9197, 18.5821], "city_center": [73.8567, 18.5204]},
}


class CabAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Cab Booking Agent",
            system_prompt=(
                "You are a cab fare estimator for India. Given a distance in km and duration "
                "in minutes, estimate a realistic Ola/Uber fare range in INR. Return ONLY a "
                "JSON object with keys: distance_km, duration_minutes, estimated_fare_min, "
                "estimated_fare_max."
            ),
        )
        self.api_key = os.getenv("OPENROUTESERVICE_API_KEY")

    def estimate(self, origin_address: str, destination_address: str) -> dict:
        """
        origin_address / destination_address are kept for compatibility with the rest
        of the app, but this demo version matches them to known city coordinates.
        """
        self.log(f"Estimating cab: {origin_address} -> {destination_address}")

        city = None
        for key in CITY_COORDS:
            if key in origin_address.lower() or key in destination_address.lower():
                city = key
                break

        if not city:
            return {"error": "City not found in coordinate list for cab estimate"}

        coords = CITY_COORDS[city]
        start = coords["airport"]
        end = coords["city_center"]

        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        headers = {"Authorization": self.api_key}
        params = {"start": f"{start[0]},{start[1]}", "end": f"{end[0]},{end[1]}"}

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as e:
            self.log(f"OpenRouteService error: {e}")
            return {"error": str(e)}

        try:
            summary = data["features"][0]["properties"]["summary"]
            distance_km = round(summary["distance"] / 1000, 1)
            duration_minutes = round(summary["duration"] / 60, 1)
        except (KeyError, IndexError):
            return {"error": "Could not calculate distance"}

        result = self.ask_gpt_json(
            f"Distance: {distance_km} km, Duration: {duration_minutes} minutes. "
            "Estimate the cab fare."
        )
        return result


if __name__ == "__main__":
    agent = CabAgent()
    result = agent.estimate("Mumbai Airport", "Mumbai City Center")
    print(result)
