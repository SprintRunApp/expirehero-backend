from importlib.metadata import metadata

import stripe

from fastapi import APIRouter, Request, HTTPException

from ..config import settings
from ..db import SessionLocal
from ..models import Team

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.stripe_webhook_secret
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    db = SessionLocal()

    try:
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            metadata = session.get("metadata") or {}

            team_id = metadata.get("team_id")
            plan = metadata.get("plan")

            if not team_id or not plan:
                return {"status": "ignored"}

            customer_id = session.get("customer")
            subscription_id = session.get("subscription")

            team = db.query(Team).filter(Team.id == int(team_id)).first()

            if team:
                team.plan = plan
                team.stripe_customer_id = customer_id
                team.stripe_subscription_id = subscription_id
                db.commit()

        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            subscription_id = subscription.get("id")

            team = (
                db.query(Team)
                .filter(Team.stripe_subscription_id == subscription_id)
                .first()
            )

            if team:
                team.plan = "canceled"
                team.stripe_subscription_id = None
                db.commit()

        elif event["type"] == "invoice.payment_failed":
            invoice = event["data"]["object"]
            subscription_id = invoice.get("subscription")

            team = (
                db.query(Team)
                .filter(Team.stripe_subscription_id == subscription_id)
                .first()
            )

            if team:
                team.plan = "past_due"
                db.commit()

    finally:
        db.close()

    return {"status": "ok"}