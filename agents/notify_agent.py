"""
Notify Agent — DUMMY VERSION.
Simulates sending SMS and Email without actually calling Twilio/SendGrid.
Perfect for demos - no signup, no API key, no real messages sent, but looks
exactly the same on screen as a real send.
"""

import time
import random
from agents.base_agent import BaseAgent


class NotifyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Notification Agent",
            system_prompt=(
                "You write short, friendly trip confirmation messages. Given itinerary details, "
                "write a concise SMS (under 300 characters) confirming the booking."
            ),
        )

    def send_sms(self, to_phone: str, itinerary_summary: str) -> dict:
        message_text = self.ask_gpt(
            f"Write a short SMS confirming this trip: {itinerary_summary}"
        )
        self.log(f"[SIMULATED] Sending SMS to {to_phone}...")
        time.sleep(1)  # fake network delay, makes the demo feel real

        fake_sid = f"SM{random.randint(10**14, 10**15 - 1)}"
        self.log(f"[SIMULATED] SMS sent. SID: {fake_sid}")

        return {
            "status": "sent",
            "sid": fake_sid,
            "message_preview": message_text,
            "note": "This is a simulated send for demo purposes - no real SMS was sent.",
        }

    def send_email(self, to_email: str, itinerary_html: str) -> dict:
        self.log(f"[SIMULATED] Sending email to {to_email}...")
        time.sleep(1)

        self.log("[SIMULATED] Email sent. Status code: 202")

        return {
            "status": "sent",
            "status_code": 202,
            "note": "This is a simulated send for demo purposes - no real email was sent.",
        }


if __name__ == "__main__":
    agent = NotifyAgent()
    print(agent.send_sms("+91XXXXXXXXXX", "Flight to Mumbai, Hotel Taj, Cab booked"))
    print(agent.send_email("test@example.com", "<p>Trip booked!</p>"))
