"""
Streamlit Frontend — this is the website itself.
Run with: streamlit run app.py
"""

import asyncio
import streamlit as st
from agents.trip_planner import TripPlannerAgent
from agents.payment_agent import PaymentAgent
from agents.notify_agent import NotifyAgent

st.set_page_config(page_title="AI Trip Planner", page_icon=":airplane:", layout="centered")

# ---------- Styling (visual only — no logic changes) ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #0E1117 0%, #14171F 100%);
    }

    /* Hero */
    .hero-wrap {
        padding: 2.2rem 1.5rem 1.6rem 1.5rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #1B2030 0%, #11141C 100%);
        border: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 1.6rem;
    }
    .hero-eyebrow {
        font-size: 0.78rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #F2A65A;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .hero-title {
        font-family: 'Fraunces', serif;
        font-size: 2.3rem;
        font-weight: 700;
        color: #F5F2EC;
        line-height: 1.15;
        margin: 0;
    }
    .hero-sub {
        color: #9AA1AE;
        font-size: 0.98rem;
        margin-top: 0.6rem;
        max-width: 540px;
    }

    /* Agent pipeline strip */
    .pipeline {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1.1rem;
    }
    .pipeline span {
        font-size: 0.74rem;
        padding: 0.28rem 0.7rem;
        border-radius: 100px;
        background: rgba(242,166,90,0.08);
        border: 1px solid rgba(242,166,90,0.25);
        color: #F2A65A;
        font-weight: 500;
    }

    /* Section dividers w/ label */
    .section-label {
        font-size: 0.78rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #6E7585;
        font-weight: 600;
        margin: 1.8rem 0 0.6rem 0;
        border-top: 1px solid rgba(255,255,255,0.08);
        padding-top: 1.2rem;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px;
        padding: 0.8rem 1rem;
    }

    .stButton button[kind="primary"] {
        background: #F2A65A;
        color: #14171F;
        border: none;
        font-weight: 600;
    }
    .stButton button[kind="primary"]:hover {
        background: #F7B978;
        color: #14171F;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Hero ----------
st.markdown(
    """
    <div class="hero-wrap">
        <div class="hero-eyebrow">Multi-agent travel desk</div>
        <p class="hero-title">Tell us the trip.<br>Let the agents handle the rest.</p>
        <p class="hero-sub">Describe where you're going in plain language. Eight specialized agents
        search flights, trains, hotels, and cabs in parallel, then hand you one itinerary to approve and pay for.</p>
        <div class="pipeline">
            <span>Flight Agent</span><span>Train Agent</span><span>Hotel Agent</span>
            <span>Cab Agent</span><span>Approval Agent</span><span>Payment Agent</span>
            <span>Notification Agent</span><span>Orchestrator</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Session state holds data across reruns (Streamlit reruns the script on every interaction)
if "itinerary" not in st.session_state:
    st.session_state.itinerary = None
if "approved" not in st.session_state:
    st.session_state.approved = False
if "paid" not in st.session_state:
    st.session_state.paid = False


# ---------- STEP 1: User request ----------
st.markdown('<div class="section-label">Step 1 — Describe your trip</div>', unsafe_allow_html=True)

user_request = st.text_area(
    "Describe your trip",
    placeholder="Book my trip from Kolkata to Mumbai, cheapest direct flight or train, "
    "3-star hotel, with cab from airport to hotel.",
    height=100,
    label_visibility="collapsed",
)

if st.button("Plan my trip", type="primary"):
    if not user_request.strip():
        st.warning("Please describe your trip first.")
    else:
        planner = TripPlannerAgent()

        with st.status("Running agents...", expanded=True) as status:
            st.write("Trip planner agent: understanding your request...")
            st.write("Flight + train + hotel + cab agents: searching in parallel...")

            result = asyncio.run(planner.plan_trip(user_request))

            st.write("Approval agent: building your itinerary...")
            status.update(label="Done! Review your itinerary below.", state="complete")

        st.session_state.itinerary = result
        st.session_state.approved = False
        st.session_state.paid = False


# ---------- STEP 2: Show itinerary + approval ----------
if st.session_state.itinerary:
    result = st.session_state.itinerary

    st.markdown('<div class="section-label">Step 2 — Review your itinerary</div>', unsafe_allow_html=True)
    st.write(result["summary"])

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total estimated cost", f"INR {result['total_cost']}")
    with col2:
        st.metric("Destination", result["details"].get("destination_city", "-"))

    if not st.session_state.approved:
        approve_col, reject_col = st.columns(2)
        with approve_col:
            if st.button("Approve and proceed to payment", type="primary"):
                st.session_state.approved = True
                st.rerun()
        with reject_col:
            if st.button("Request changes"):
                st.session_state.itinerary = None
                st.rerun()


# ---------- STEP 3: Payment (Razorpay test mode) ----------
if st.session_state.itinerary and st.session_state.approved and not st.session_state.paid:
    st.markdown('<div class="section-label">Step 3 — Payment</div>', unsafe_allow_html=True)
    st.info("This is TEST MODE - no real money will be charged.")

    if st.button("Pay now (test)", type="primary"):
        payment_agent = PaymentAgent()
        order = payment_agent.create_order(st.session_state.itinerary["total_cost"])

        if "error" in order:
            st.error(f"Payment error: {order['error']}")
        else:
            st.session_state.paid = True
            st.session_state.order = order
            st.rerun()


# ---------- STEP 4: Confirmation + notification ----------
if st.session_state.paid:
    st.markdown('<div class="section-label">Step 4 — Confirmation</div>', unsafe_allow_html=True)
    st.success("Payment successful! Your trip is booked.")
    st.write(f"Order ID: {st.session_state.order['order_id']}")

    st.subheader("Send confirmation")
    notify_col1, notify_col2 = st.columns(2)

    with notify_col1:
        phone = st.text_input("Phone number (with country code)", placeholder="+91XXXXXXXXXX")
        if st.button("Send SMS confirmation"):
            if phone:
                notify_agent = NotifyAgent()
                sms_result = notify_agent.send_sms(phone, st.session_state.itinerary["summary"])
                if "error" in sms_result:
                    st.error(sms_result["error"])
                else:
                    st.success("SMS sent!")

    with notify_col2:
        email = st.text_input("Email address", placeholder="you@example.com")
        if st.button("Send email confirmation"):
            if email:
                notify_agent = NotifyAgent()
                email_result = notify_agent.send_email(
                    email, f"<p>{st.session_state.itinerary['summary']}</p>"
                )
                if "error" in email_result:
                    st.error(email_result["error"])
                else:
                    st.success("Email sent!")
