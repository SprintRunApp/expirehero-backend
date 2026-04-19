import stripe

from fastapi import APIRouter, Request

from ..config import settings
from ..db import SessionLocal
from ..models import UserProfile

router = APIRouter()


@router.post("/stripe")

async def stripe_webhook(request: Request):

    payload = await request.body()

    sig_header = request.headers.get("stripe-signature")

    event = stripe.Webhook.construct_event(
        payload,
        sig_header,
        settings.stripe_webhook_secret
    )

    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        user_id = session["metadata"]["user_id"]

        db = SessionLocal()

        user = db.query(UserProfile).get(user_id)

        if user:
            user.plan = "pro"
            db.commit()

        db.close()

    return {"status": "ok"}