import stripe

from ..config import settings

stripe.api_key = settings.stripe_secret_key


def get_price_id(plan: str) -> str:
    if plan == "starter":
        return settings.stripe_starter_price_id

    if plan == "pro":
        return settings.stripe_pro_price_id

    if plan == "business":
        return settings.stripe_business_price_id

    raise ValueError("Invalid plan")


def create_checkout_session(
    team_id: int,
    plan: str,
    success_path: str | None = None,
    cancel_path: str | None = None,
):
    price_id = get_price_id(plan)

    success_url = (
        f"{settings.frontend_url}{success_path}"
        if success_path
        else f"{settings.frontend_url}/success"
    )

    cancel_url = (
        f"{settings.frontend_url}{cancel_path}"
        if cancel_path
        else f"{settings.frontend_url}/cancel"
    )

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",

        line_items=[
            {
                "price": price_id,
                "quantity": 1
            }
        ],

        success_url=success_url,
        cancel_url=cancel_url,

        metadata={
            "team_id": str(team_id),
            "plan": plan
        },

        subscription_data={
            "metadata": {
                "team_id": str(team_id),
                "plan": plan
            }
        }
    )

    return session.url