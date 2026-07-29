from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session, joinedload

from ..models import Reminder, Item, Notification
from .notification_recipients import get_recipients
from .email_builder import build_email_subject, build_email_body
from .email_service import email_service
from .protection_engine import (
    get_protection_days,
    resolve_protection_stage,
)

def get_matching_trigger_days(
    reminder: Reminder,
    today: date,
) -> int | None:
    protection_days = get_protection_days(reminder)

    for days in protection_days:
        trigger_date = reminder.due_date - timedelta(days=days)

        if trigger_date == today:
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

        if reminder.item.archived:
            print("⏭️ SKIP archived workflow")
            continue

        if reminder.item.status != "active":
            print(
                f"⏭️ SKIP workflow status: "
                f"{reminder.item.status}"
            )
            continue

        trigger_days = get_matching_trigger_days(reminder, today)

        if trigger_days is None:
            print("⏭️ SKIP (not today)")
            continue

        item = reminder.item

        stage = resolve_protection_stage(
            reminder=reminder,
            trigger_days=trigger_days,
        )

        recipients = get_recipients(
            item=item,
            db=db,
            stage=stage,
        )

        print(f"📨 Recipients: {[u.email for u in recipients]}")

        if not recipients:
            continue

        subject = build_email_subject(
            item=item,
            due_date=reminder.due_date,
            stage=stage,
        )

        body = build_email_body(
            reminder=reminder,
            item=item,
            stage=stage,
        )

        print(
            f"🛡️ Protection level "
            f"{stage.level}/{stage.total_levels} | "
            f"{stage.severity} | "
            f"{stage.trigger_days} days before deadline"
        )

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