from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..db import get_db
from ..deps import get_current_user
from ..models import UserProfile, Team
from ..schemas import UserMe

router = APIRouter()


class AuthPayload(BaseModel):
    full_name: str | None = None
    company_name: str | None = None
    industry: str | None = None
    region: str | None = None


@router.get("/me", response_model=UserMe)
def me(
    current_user: UserProfile = Depends(get_current_user)
):
    return current_user


@router.post("/me", response_model=UserMe)
def me_post(
    payload: AuthPayload,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    # Update the user's name when provided.
    if payload.full_name:
        current_user.name = payload.full_name

    # Create a team for a new owner.
    if (
        payload.company_name
        and not current_user.owned_team
        and not current_user.team_membership
    ):
        team = Team(
            name=payload.company_name,
            owner_id=current_user.id,
            industry=payload.industry,
            region=payload.region
        )

        db.add(team)
        db.flush()

    # Fill missing onboarding data for an existing team.
    if current_user.owned_team:
        if payload.industry and not current_user.owned_team.industry:
            current_user.owned_team.industry = payload.industry

        if payload.region and not current_user.owned_team.region:
            current_user.owned_team.region = payload.region

    db.commit()
    db.refresh(current_user)

    return current_user


@router.post("/upgrade")
def upgrade_plan(
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    current_user.plan = "pro"
    db.commit()

    return {"status": "upgraded"}