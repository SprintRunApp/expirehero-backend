from datetime import date

from ..models import Reminder, Item


def compute_notification_status(due_date: date) -> tuple[str, int]:
    today = date.today()
    diff = (due_date - today).days

    if diff < 0:
        return "expired", diff
    if diff <= 7:
        return "urgent", diff
    if diff <= 30:
        return "soon", diff
    return "normal", diff


def build_email_subject(item: Item, due_date: date) -> str:
    status, diff = compute_notification_status(due_date)

    if status == "expired":
        return f"[EXPIRED] {item.title} has expired"

    if status == "urgent":
        if diff == 0:
            return f"[URGENT] {item.title} expires today"
        if diff == 1:
            return f"[URGENT] {item.title} expires in 1 day"
        return f"[URGENT] {item.title} expires in {diff} days"

    if status == "soon":
        if diff == 1:
            return f"Reminder: {item.title} expires in 1 day"
        return f"Reminder: {item.title} expires in {diff} days"

    return f"Reminder: {item.title}"


def build_email_body(reminder: Reminder, item: Item) -> str:
    status, diff = compute_notification_status(reminder.due_date)

    if status == "expired":
        status_text = "Expired"
    elif status == "urgent":
        status_text = "Urgent"
    elif status == "soon":
        status_text = "Expiring soon"
    else:
        status_text = "Reminder"

    assigned_to = item.assigned_user.name if getattr(item, "assigned_user", None) else "Unassigned"

    body = f"""Hello,

This is a reminder about: "{item.title}"

Category: {item.category or "—"}
Assigned to: {assigned_to}
Due date: {reminder.due_date.strftime("%Y-%m-%d")}
Status: {status_text}

Please take action to avoid issues.

Open dashboard:
https://expireheros.app/dashboard

– ExpireHero
"""
    return body