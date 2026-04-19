from datetime import date
from sqlalchemy.orm import Session, joinedload

from ..models import Reminder, Item
from .notification_recipients import get_recipients
from .email_builder import build_email_subject, build_email_body
from .email_service import email_service


from datetime import timedelta

def should_send_today(reminder: Reminder, today: date) -> bool:
    if not reminder.advance_days:
        return False

    for days in reminder.advance_days:
        if reminder.due_date - timedelta(days=days) == today:
            return True

    return False


def run_reminders(db: Session) -> dict:
    today = date.today()

    reminders = (
        db.query(Reminder)
        .options(
            joinedload(Reminder.item).joinedload(Item.owner),
            joinedload(Reminder.item).joinedload(Item.assigned_user),
        )
        .all()
    )

    sent_count = 0
    checked_count = 0

    for reminder in reminders:
        checked_count += 1

        print(f"🔍 Checking reminder: {reminder.item.title if reminder.item else 'NO ITEM'} | due: {reminder.due_date}")

        if reminder.status != "active":
            continue

        if not reminder.item:
            continue

        if not should_send_today(reminder, today):
            print("⏭️ SKIP (not today)")
            continue

        item = reminder.item
        recipients = get_recipients(item, db)

        print(f"📨 Recipients: {[u.email for u in recipients]}")

        if not recipients:
            continue

        subject = build_email_subject(item, reminder.due_date)
        body = build_email_body(reminder, item)

        for user in recipients:
            if not user.email:
                continue

            email_service.send_email(
                to_email=user.email,
                subject=subject,
                content=body
            )
            sent_count += 1

    return {
        "status": "ok",
        "checked_reminders": checked_count,
        "sent_emails": sent_count,
    }