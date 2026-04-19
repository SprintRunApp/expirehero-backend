from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from .firebase_auth import verify_firebase_token
from .db import get_db
from .models import UserProfile
from .models import Team



security = HTTPBearer()


def get_current_user(
    token=Depends(security),
    db: Session = Depends(get_db)
) -> UserProfile:

    try:
        decoded = verify_firebase_token(token.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    firebase_uid = decoded["uid"]
    email = decoded.get("email")

    from sqlalchemy.orm import joinedload

    user = (
        db.query(UserProfile)
        .options(
            joinedload(UserProfile.owned_team),
            joinedload(UserProfile.team_membership)
        )
    .filter(UserProfile.firebase_uid == firebase_uid)
    .first()
    )

    # 🔥 AUTO TEAM (only for owner)
    if user and not user.owned_team and not user.team_membership:
        team_name = user.email.split("@")[0] + "'s Team"

        team = Team(
            name=team_name,
            owner_id=user.id
        )

        db.add(team)
        db.commit()
        db.refresh(team)

        # 🔥 odśwież usera żeby miał team
        user = (
            db.query(UserProfile)
            .options(
                joinedload(UserProfile.owned_team),
                joinedload(UserProfile.team_membership)
            )
            .filter(UserProfile.id == user.id)
            .first()
        )

    if not user:
        user = UserProfile(
            firebase_uid=firebase_uid,
            email=email
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user