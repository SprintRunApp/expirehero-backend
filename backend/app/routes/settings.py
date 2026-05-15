from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user
from ..models import UserProfile, Team, TeamMember

router = APIRouter()


@router.delete("/me", status_code=204)
def delete_account(
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    # 🔥 jeśli owner → usuń cały team
    if current_user.owned_team:
        db.delete(current_user.owned_team)

    # 🔥 jeśli member → usuń membership
    if current_user.team_membership:
        db.delete(current_user.team_membership)

    # 🔥 usuń usera (cascade usunie items itd)
    db.delete(current_user)
    db.commit()

    return None