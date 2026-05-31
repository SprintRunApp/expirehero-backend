from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session, joinedload

from ..models import Reminder, Item, Notification
from .notification_recipients import get_recipients
from .email_builder import build_email_subject, build_email_body
from .email_service import email_service


def get_matching_trigger_days(reminder: Reminder, today: date) -> int | None:
    if not reminder.advance_days:
        return None

    for days in reminder.advance_days:
        if reminder.due_date - timedelta(days=days) == today:
            return days

    return None


def run_reminders(db: Session) -> dict:
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
    skipped_duplicates = 0
    failed_count = 0

    for reminder in reminders:
        checked_count += 1

        timezone = reminder.timezone or "UTC"
        today = datetime.now(ZoneInfo(timezone)).date()

        print(
            f"🔍 Checking reminder: "
            f"{reminder.item.title if reminder.item else 'NO ITEM'} | "
            f"due: {reminder.due_date} | timezone: {timezone} | today: {today}"
        )

        if reminder.status != "active":
            continue

        if not reminder.item:
            continue

        trigger_days = get_matching_trigger_days(reminder, today)

        if trigger_days is None:
            print("⏭️ SKIP (not today)")
            continue

        item = reminder.item
        recipients = get_recipients(item, db)

        print(f"📨 Recipients: {[u.email for u in recipients]}")

        if not recipients:
            continue

        subject = build_email_subject(
            item,
            reminder.due_date,
            reminder.timezone
        )

        body = build_email_body(reminder, item)

        for user in recipients:
            if not user.email:
                continue

            existing = (
                db.query(Notification)
                .filter(
                    Notification.reminder_id == reminder.id,
                    Notification.channel == "email",
                    Notification.recipient_email == user.email,
                    Notification.trigger_days == trigger_days,
                    Notification.due_date == reminder.due_date,
                    Notification.status == "sent",
                )
                .first()
            )

            if existing:
                print(f"⏭️ SKIP duplicate email to {user.email}")
                skipped_duplicates += 1
                continue

            notification = Notification(
                reminder_id=reminder.id,
                recipient_email=user.email,
                recipient_user_id=user.id,
                channel="email",
                trigger_days=trigger_days,
                due_date=reminder.due_date,
                scheduled_at=datetime.utcnow(),
                status="pending",
            )

            db.add(notification)
            db.commit()
            db.refresh(notification)

            try:
                email_service.send_email(
                    to_email=user.email,
                    subject=subject,
                    content=body
                )

                notification.status = "sent"
                notification.sent_at = datetime.utcnow()
                notification.error = None

                sent_count += 1
                print(f"✅ EMAIL SENT to {user.email}")

            except Exception as e:
                notification.status = "failed"
                notification.error = str(e)
                failed_count += 1

                print(f"❌ EMAIL FAILED to {user.email}: {e}")

            db.commit()

    return {
        "status": "ok",
        "checked_reminders": checked_count,
        "sent_emails": sent_count,
        "failed_emails": failed_count,
        "skipped_duplicates": skipped_duplicates,
    }