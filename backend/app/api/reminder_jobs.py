from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import traceback

from ..db import get_db
from ..services.reminder_engine import run_reminders

router = APIRouter()


@router.post("/run")
def run_job(db: Session = Depends(get_db)):
    try:
        return run_reminders(db)
    except Exception as e:
        print("❌ JOB ERROR:", str(e))
        print(traceback.format_exc())

        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }