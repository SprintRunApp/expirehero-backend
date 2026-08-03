from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session, joinedload

from ..models import Reminder, Item, Notification
from .notification_recipients import get_recipients
from .email_builder import (
    build_email_subject,
    build_email_body,
    build_external_email_subject,
    build_external_email_body,
)
from .email_service import email_service
from .protection_engine import (
    get_protection_days,
    resolve_protection_stage,
)

def get_today_for_timezone(timezone: str) -> date:
    try:
        return datetime.now(
            ZoneInfo(timezone or "UTC")
        ).date()

    except Exception:
        print(
            f"⚠️ Invalid timezone '{timezone}', "
            f"falling back to UTC"
        )

        return datetime.now(
            ZoneInfo("UTC")
        ).date()

def get_matching_trigger_days(
    reminder: Reminder,
    today: date,
) -> int | None:
    protection_days = get_protection_days(reminder)

    days_remaining = (
        reminder.due_date - today
    ).days

    # Nigdy nie uruchamiamy ochrony
    # w dniu terminu ani po terminie.
    if days_remaining <= 0:
        return None

    # Szukamy najbliższego poziomu ochrony,
    # który powinien już być aktywny.
    for trigger_days in sorted(protection_days):
        if days_remaining <= trigger_days:
            return trigger_days

    return None


def send_external_action_email(
    db: Session,
    reminder: Reminder,
    item: Item,
    stage,
) -> bool:
    if not item.external_email_enabled:
        return False

    contact = item.external_contact

    if not contact:
        print("⚠️ External email enabled but no external contact")
        return False

    if not contact.active:
        print("⚠️ External contact is inactive")
        return False

    if not contact.email:
        print("⚠️ External contact has no email address")
        return False

    existing = (
        db.query(Notification)
        .filter(
            Notification.reminder_id == reminder.id,
            Notification.channel == "external_email",
            Notification.recipient_email == contact.email,
            Notification.due_date == reminder.due_date,
            Notification.status == "sent",
        )
        .first()
    )

    if existing:
        print(
            f"⏭️ External email already sent to "
            f"{contact.email} for this deadline"
        )
        return False

    subject = build_external_email_subject(
        reminder=reminder,
        item=item,
    )

    body = build_external_email_body(
        reminder=reminder,
        item=item,
        stage=stage,
    )

    notification = Notification(
        reminder_id=reminder.id,
        recipient_email=contact.email,
        recipient_user_id=None,
        channel="external_email",
        trigger_days=stage.trigger_days,
        due_date=reminder.due_date,
        scheduled_at=datetime.utcnow(),
        status="pending",
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    try:
        owner_email = (
            item.owner.email
            if item.owner and item.owner.email
            else None
        )

        email_service.send_email(
            to_email=contact.email,
            cc_email=owner_email,
            subject=subject,
            content=body,
        )

        notification.status = "sent"
        notification.sent_at = datetime.utcnow()
        notification.error = None

        db.commit()

        print(
            f"✅ EXTERNAL EMAIL SENT to {contact.email}"
        )

        return True

    except Exception as e:
        notification.status = "failed"
        notification.error = str(e)

        db.commit()

        print(
            f"❌ EXTERNAL EMAIL FAILED to "
            f"{contact.email}: {e}"
        )

        return False

def run_reminders(db: Session) -> dict:
    reminders = (
        db.query(Reminder)
        .options(
            joinedload(Reminder.item).joinedload(Item.owner),
            joinedload(Reminder.item).joinedload(Item.assigned_user),
            joinedload(Reminder.item).joinedload(Item.workflow_group),
            joinedload(Reminder.item).joinedload(Item.external_contact),
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
        today = get_today_for_timezone(timezone)

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
            print("⏭️ SKIP (no protection action required)")
            continue

        item = reminder.item

        stage = resolve_protection_stage(
            reminder=reminder,
            trigger_days=trigger_days,
        )

        send_external_action_email(
            db=db,
            reminder=reminder,
            item=item,
            stage=stage,
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