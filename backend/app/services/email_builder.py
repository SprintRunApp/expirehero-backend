from datetime import date

from ..models import Reminder, Item
from .protection_engine import ProtectionStage


def build_email_subject(
    item: Item,
    due_date: date,
    stage: ProtectionStage,
) -> str:
    days = stage.trigger_days
    day_text = "1 day" if days == 1 else f"{days} days"

    if stage.severity == "critical":
        return (
            f"[CRITICAL] Immediate action required: "
            f"{item.title} expires in {day_text}"
        )

    if stage.severity == "urgent":
        return (
            f"[URGENT] {item.title} expires in {day_text}"
        )

    if stage.severity == "warning":
        return (
            f"[ACTION REQUIRED] {item.title} expires in {day_text}"
        )

    return (
        f"[PROTECTION] {item.title} expires in {day_text}"
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

    headline, message, action_text = get_stage_message(
        item=item,
        stage=stage,
        days_text=days_text,
    )

    return f"""Hello,

{headline}

{message}

Workflow: {item.title}
Category: {item.category or "—"}
Workflow group: {group_name}
Assigned to: {assigned_to}

Due date: {reminder.due_date.strftime("%Y-%m-%d")}
Time remaining: {days_text}
Protection level: {stage.level} of {stage.total_levels}
Protection status: {stage.label}

{action_text}

Completing this workflow will stop all remaining protection alerts for this deadline.

Open ExpireHeros:
https://www.expireheros.app

– ExpireHeros Protection Engine
"""


def get_stage_message(
    item: Item,
    stage: ProtectionStage,
    days_text: str,
) -> tuple[str, str, str]:

    if stage.severity == "critical":
        return (
            "CRITICAL DEADLINE ALERT",
            (
                f'The deadline for "{item.title}" is now only '
                f"{days_text} away."
            ),
            (
                "Immediate action is required. "
                "This is the final protection alert before the deadline."
            ),
        )

    if stage.severity == "urgent":
        return (
            "URGENT ACTION REQUIRED",
            (
                f'The deadline for "{item.title}" is approaching rapidly. '
                f"Only {days_text} remain."
            ),
            (
                "Please make sure this workflow is completed immediately. "
                "The company owner has also been included in this protection stage."
            ),
        )

    if stage.severity == "warning":
        return (
            "ACTION REQUIRED",
            (
                f'The workflow "{item.title}" has not yet been completed '
                f"and the deadline is now {days_text} away."
            ),
            (
                "Please review the workflow and make sure the required action "
                "is completed before the deadline."
            ),
        )

    return (
        "DEADLINE PROTECTION STARTED",
        (
            f'ExpireHeros has started protecting the deadline for "{item.title}". '
            f"There are currently {days_text} remaining."
        ),
        (
            "No urgent escalation is required yet, but we recommend preparing "
            "the necessary action early."
        ),
    )

def build_external_email_subject(
    reminder: Reminder,
    item: Item,
) -> str:
    return (
        f"Action required: {item.title} "
        f"before {reminder.due_date.strftime('%Y-%m-%d')}"
    )


def build_external_email_body(
    reminder: Reminder,
    item: Item,
    stage: ProtectionStage,
) -> str:
    contact = item.external_contact

    contact_name = (
        contact.contact_name
        if contact and contact.contact_name
        else "Sir or Madam"
    )

    days_text = (
        "1 day"
        if stage.trigger_days == 1
        else f"{stage.trigger_days} days"
    )

    default_message = f"""Hello {contact_name},

We are contacting you regarding:

{item.title}

The deadline is {reminder.due_date.strftime("%Y-%m-%d")}.

There are currently {days_text} remaining.

Please contact us to arrange the required service or action before the deadline.

Thank you.

– Sent automatically by ExpireHeros
"""

    template = (
        item.external_email_template.strip()
        if item.external_email_template
        else None
    )

    if not template:
        return default_message

    replacements = {
        "{contact_name}": contact_name,
        "{company_name}": (
            contact.company_name
            if contact
            else ""
        ),
        "{workflow_title}": item.title,
        "{category}": item.category or "",
        "{due_date}": reminder.due_date.strftime("%Y-%m-%d"),
        "{days_remaining}": str(stage.trigger_days),
    }

    content = template

    for placeholder, value in replacements.items():
        content = content.replace(
            placeholder,
            value,
        )

    return content