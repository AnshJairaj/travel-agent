"""
Base Agent class - every agent (Flight, Train, Hotel, Cab, etc.) inherits from this.
It handles talking to Groq (fast inference, generous free tier) so each child agent
doesn't repeat that code.

Groq's API is OpenAI-compatible, so we still use the `openai` Python package -
we just point it at Groq's base_url and use a Groq model name instead.
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

GROQ_MODEL = "llama-3.3-70b-versatile"  # check https://console.groq.com/docs/models for current options


class BaseAgent:
    """
    Parent class for all agents.
    Each child agent sets its own `name` and `system_prompt`,
    then calls self.ask_gpt() whenever it needs the AI to think/decide/format something.
    """

    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt

    def ask_gpt(self, user_message: str, json_mode: bool = False) -> str:
        """
        Sends a message to Groq and returns the text response.
        Set json_mode=True when you want Groq to return clean JSON only.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]

        kwargs = {
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": 0.3,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def ask_gpt_json(self, user_message: str) -> dict:
        """
        Same as ask_gpt but parses the result into a Python dict.
        Use this when you need structured data back (e.g. {"price": 4500, "airline": "IndiGo"})
        """
        raw = self.ask_gpt(user_message, json_mode=True)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"error": "Could not parse JSON", "raw": raw}

    def log(self, message: str):
        """Simple console logger so you can see what each agent is doing during a run."""
        print(f"[{self.name}] {message}")
