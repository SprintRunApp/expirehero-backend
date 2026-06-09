from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session, joinedload

from .firebase_auth import verify_firebase_token
from .db import get_db
from .models import UserProfile


security = HTTPBearer()


def load_user_with_relations(db: Session, user_id: str):
    return (
        db.query(UserProfile)
        .options(
            joinedload(UserProfile.owned_team),
            joinedload(UserProfile.team_membership)
        )
        .filter(UserProfile.id == user_id)
        .first()
    )


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

    user = (
        db.query(UserProfile)
        .options(
            joinedload(UserProfile.owned_team),
            joinedload(UserProfile.team_membership)
        )
        .filter(UserProfile.firebase_uid == firebase_uid)
        .first()
    )

    if not user and email:
        user = (
            db.query(UserProfile)
            .options(
                joinedload(UserProfile.owned_team),
                joinedload(UserProfile.team_membership)
            )
            .filter(UserProfile.email == email)
            .first()
        )

        if user:
            user.firebase_uid = firebase_uid
            db.commit()
            user = load_user_with_relations(db, user.id)

    if not user:
        user = UserProfile(
            firebase_uid=firebase_uid,
            email=email
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        user = load_user_with_relations(db, user.id)

    return user