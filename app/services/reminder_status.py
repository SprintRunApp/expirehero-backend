from datetime import date


def compute_days_left(due_date: date) -> int:
    today = date.today()
    return (due_date - today).days


def compute_ui_status(due_date: date) -> str:
    days_left = compute_days_left(due_date)

    if days_left < 0:
        return "red"

    if days_left == 0:
        return "red"

    if days_left <= 30:
        return "yellow"

    return "green"