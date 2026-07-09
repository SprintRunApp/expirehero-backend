from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..deps import get_current_user
from ..services.stripe_service import create_checkout_session

router = APIRouter()


class CheckoutRequest(BaseModel):
    plan: str


@router.post("/create-checkout-session")
def create_session(
    payload: CheckoutRequest,
    current_user=Depends(get_current_user)
):
    team = current_user.owned_team

    if not team:
        raise HTTPException(
            status_code=400,
            detail="You need to create a company/team before subscribing."
        )

    if payload.plan not in ["starter", "pro", "business"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid plan."
        )

    url = create_checkout_session(
        team_id=team.id,
        plan=payload.plan
    )

    return {"checkout_url": url}