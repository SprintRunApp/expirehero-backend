from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..services.reminder_engine import run_reminders

router = APIRouter()


@router.post("/run")
def run_job(db: Session = Depends(get_db)):
    return run_reminders(db)

@router.get("/test-email")
def test_email():
    from app.services.email_service import email_service

    email_service.send_email(
        to_email="krzschramm@gmail.com",
        subject="ExpireHero TEST 🚀",
        content="Jeśli to widzisz — działa 💥"
    )

    return {"status": "sent"}