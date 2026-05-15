from datetime import date, timedelta

from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import Reminder
from ..redis_client import email_queue


def run_scheduler():

    db: Session = SessionLocal()

    today = date.today()

    reminders = db.query(Reminder).all()

    for r in reminders:

        for advance in r.advance_days:

            if r.due_date - timedelta(days=advance) == today:

                email_queue.enqueue(
                    "app.workers.email_worker.process_reminder",
                    r.id
                )

    db.close()