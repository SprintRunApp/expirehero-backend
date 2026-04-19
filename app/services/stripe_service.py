import stripe

from ..config import settings

stripe.api_key = settings.stripe_secret_key


def create_checkout_session(user_id):

    session = stripe.checkout.Session.create(

        payment_method_types=["card"],

        mode="payment",

        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": "Expire Hero PRO"
                },
                "unit_amount": 900
            },
            "quantity": 1
        }],

        success_url=f"{settings.frontend_url}/success",
        cancel_url=f"{settings.frontend_url}/cancel",

        metadata={
            "user_id": user_id
        }

    )

    return session.url