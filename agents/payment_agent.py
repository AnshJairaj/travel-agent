"""
Payment Agent — creates a Razorpay order in TEST MODE.
No real money moves. Returns an order_id and a payment link you can show in the demo.
"""

import os
import razorpay
from dotenv import load_dotenv
from agents.base_agent import BaseAgent

load_dotenv()


class PaymentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Payment Agent",
            system_prompt=(
                "You are a payment confirmation assistant. Given a Razorpay order response, "
                "summarize it in one friendly sentence for the user."
            ),
        )
        self.client = razorpay.Client(
            auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
        )

    def create_order(self, amount_inr: float, receipt_id: str = "trip_booking") -> dict:
        """
        amount_inr: total trip cost in rupees (e.g. 5400.00)
        Razorpay needs amount in paise (1 INR = 100 paise)
        """
        self.log(f"Creating test payment order for INR {amount_inr}")

        amount_paise = int(amount_inr * 100)

        try:
            order = self.client.order.create(
                {
                    "amount": amount_paise,
                    "currency": "INR",
                    "receipt": receipt_id,
                    "payment_capture": 1,
                }
            )
        except Exception as e:
            self.log(f"Razorpay error: {e}")
            return {"error": str(e)}

        return {
            "order_id": order["id"],
            "amount": amount_inr,
            "currency": "INR",
            "status": order["status"],
            "key_id": os.getenv("RAZORPAY_KEY_ID"),  # needed by frontend checkout
        }


if __name__ == "__main__":
    agent = PaymentAgent()
    result = agent.create_order(5400.00)
    print(result)
