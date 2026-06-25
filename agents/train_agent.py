"""
Train Agent — calls RapidAPI's Indian Railways endpoint to search trains,
then uses GPT to pick the best option and format it.
"""

import os
import httpx
from dotenv import load_dotenv
from agents.base_agent import BaseAgent

load_dotenv()

STATION_CODES = {
    "kolkata": "HWH",
    "mumbai": "CSTM",
    "delhi": "NDLS",
    "bangalore": "SBC",
    "chennai": "MAS",
    "hyderabad": "SC",
    "pune": "PUNE",
}


class TrainAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Train Search Agent",
            system_prompt=(
                "You are a train search assistant. Given raw train search results in JSON, "
                "pick the cheapest train with the shortest duration. Return ONLY a JSON object "
                "with keys: train_name, train_number, departure_time, arrival_time, duration, "
                "price, class_type."
            ),
        )
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        # Example host - replace with the exact host shown on your chosen RapidAPI train API page
        self.api_host = "irctc1.p.rapidapi.com"

    def search(self, origin_city: str, destination_city: str, date: str) -> dict:
        origin_code = STATION_CODES.get(origin_city.lower())
        dest_code = STATION_CODES.get(destination_city.lower())

        if not origin_code or not dest_code:
            return {"error": f"Unknown station code for {origin_city} or {destination_city}"}

        self.log(f"Searching trains {origin_code} -> {dest_code} on {date}")

        url = f"https://{self.api_host}/api/v3/trainBetweenStations"
        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": self.api_host,
        }
        params = {
            "fromStationCode": origin_code,
            "toStationCode": dest_code,
            "dateOfJourney": date,
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as e:
            self.log(f"RapidAPI error: {e}")
            return {"error": str(e)}

        trains = data.get("data", [])
        if not trains:
            return {"error": "No trains found"}

        result = self.ask_gpt_json(
            f"Here are train options: {trains[:5]}. Pick the best one (cheap + fast)."
        )
        return result


if __name__ == "__main__":
    agent = TrainAgent()
    result = agent.search("Kolkata", "Mumbai", "2026-07-15")
    print(result)
