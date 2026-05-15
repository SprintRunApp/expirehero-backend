from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..deps import get_current_user
from ..models import UserProfile, Team
from ..schemas import UserMe
from app.deps import get_db


from ..db import get_db
from ..services.reminder_engine import run_reminders

router = APIRouter()




# 🔥 payload do onboardingu
class AuthPayload(BaseModel):
    full_name: str | None = None
    company_name: str | None = None


# ✅ STANDARDOWE /me (GET)
@router.get("/me", response_model=UserMe)
def me(current_user: UserProfile = Depends(get_current_user)):
    return current_user


# 🔥 NOWE /me (POST) — onboarding + auto team
@router.post("/me", response_model=UserMe)
def me_post(
    payload: AuthPayload,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    # 🔥 jeśli user nie ma teamu → twórz
    # 🔥 CREATE TEAM (jeśli brak)
    if not current_user.owned_team and not current_user.team_membership:

        team_name = payload.company_name or current_user.name or "My Team"

        team = Team(
            name=team_name,
            owner_id=current_user.id
        )

        db.add(team)
        db.commit()

        # 🔥 UPDATE TEAM NAME (JEŚLI PODANY COMPANY)
        if payload.company_name and current_user.owned_team:
            current_user.owned_team.name = payload.company_name
            db.commit()

    return current_user


# 🔥 upgrade (zostaje bez zmian)
@router.post("/upgrade")
def upgrade_plan(
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    current_user.plan = "pro"
    db.commit()

    return {"status": "upgraded"}
