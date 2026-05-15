from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import Reminder, Item
from ..services.email_service import send_email


def process_reminder(reminder_id):

    db: Session = SessionLocal()

    reminder = db.query(Reminder).get(reminder_id)

    item = db.query(Item).get(reminder.item_id)

    email = item.owner.email

    subject = f"Reminder: {item.title}"

    body = f"""
    <h2>Expire Hero Reminder</h2>

    <p>{item.title} expires on {reminder.due_date}</p>

    """

    send_email(email, subject, body)

    db.close()