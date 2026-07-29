from datetime import date

from ..models import Reminder, Item
from .protection_engine import ProtectionStage


def build_email_subject(
    item: Item,
    due_date: date,
    stage: ProtectionStage,
) -> str:
    days = stage.trigger_days

    if stage.severity == "critical":
        prefix = "[CRITICAL]"
    elif stage.severity == "urgent":
        prefix = "[URGENT]"
    elif stage.severity == "warning":
        prefix = "[ACTION REQUIRED]"
    else:
        prefix = "[PROTECTION]"

    day_text = "1 day" if days == 1 else f"{days} days"

    return (
        f"{prefix} {item.title} expires in {day_text}"
    )


def build_email_body(
    reminder: Reminder,
    item: Item,
    stage: ProtectionStage,
) -> str:
    assigned_to = (
        item.assigned_user.name
        if getattr(item, "assigned_user", None)
        else "Unassigned"
    )

    group_name = (
        item.workflow_group.name
        if getattr(item, "workflow_group", None)
        else "No workflow group"
    )

    days_text = (
        "1 day"
        if stage.trigger_days == 1
        else f"{stage.trigger_days} days"
    )

    return f"""Hello,

ExpireHeros is protecting your company from a missed deadline.

Workflow: {item.title}
Category: {item.category or "—"}
Workflow group: {group_name}
Assigned to: {assigned_to}

Due date: {reminder.due_date.strftime("%Y-%m-%d")}
Time remaining: {days_text}
Protection level: {stage.level} of {stage.total_levels}
Protection status: {stage.label}
Timezone: {reminder.timezone or "UTC"}

Action is required before the due date.

Completing this workflow now will stop all remaining protection alerts.

Open dashboard:
https://www.expireheros.app

– ExpireHeros Protection Engine
"""