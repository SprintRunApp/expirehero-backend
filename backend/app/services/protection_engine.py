from dataclasses import dataclass

from ..models import Reminder


@dataclass(frozen=True)
class ProtectionStage:
    trigger_days: int
    level: int
    total_levels: int
    severity: str
    label: str


def get_protection_days(reminder: Reminder) -> list[int]:
    """
    Zwraca unikalne poziomy ochrony, posortowane od najwcześniejszego.

    Dni 0 i wartości ujemne są ignorowane, ponieważ ExpireHeros
    ma zapobiegać wygaśnięciu przed terminem.
    """
    if not reminder.advance_days:
        return []

    return sorted(
        {
            int(days)
            for days in reminder.advance_days
            if int(days) > 0
        },
        reverse=True,
    )


def resolve_protection_stage(
    reminder: Reminder,
    trigger_days: int,
) -> ProtectionStage:
    protection_days = get_protection_days(reminder)

    if trigger_days not in protection_days:
        raise ValueError(
            f"Trigger day {trigger_days} is not part of the protection plan."
        )

    level = protection_days.index(trigger_days) + 1
    total_levels = len(protection_days)

    if total_levels == 1:
        severity = "critical"
        label = "Final protection alert"

    elif level == total_levels:
        severity = "critical"
        label = "Final protection alert"

    elif level == total_levels - 1:
        severity = "urgent"
        label = "Urgent protection alert"

    elif level == 1:
        severity = "initial"
        label = "Protection started"

    else:
        severity = "warning"
        label = "Protection escalation"

    return ProtectionStage(
        trigger_days=trigger_days,
        level=level,
        total_levels=total_levels,
        severity=severity,
        label=label,
    )