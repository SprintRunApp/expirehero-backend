from fastapi import APIRouter, Depends

from ..deps import get_current_user
from ..services.stripe_service import create_checkout_session

router = APIRouter()


@router.post("/create-checkout-session")
def create_session(current_user = Depends(get_current_user)):

    url = create_checkout_session(str(current_user.id))

    return {"checkout_url": url}