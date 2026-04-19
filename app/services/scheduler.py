from datetime import datetime
from app.models import Reminder
from app.services.email import send_email


def check_and_send(db):
    reminders = db.query(Reminder).all()

    today = datetime.utcnow().date()

    for r in reminders:
        if r.due_date == today:
            send_email(
                to_email="test@example.com",
                subject="Reminder!",
                content=f"{r.item.title} expires today!"
            )