from sqlalchemy.orm import Session

from ..models import Reminder, Item
from ..config import settings


ACTIVE_PLANS = ["starter", "pro", "business"]


def get_user_team(user):
    if user.owned_team:
        return user.owned_team

    if user.team_membership:
        return user.team_membership.team

    return None


def get_reminder_limit(plan: str):
    if plan == "starter":
        return 50

    if plan == "pro":
        return 200

    if plan == "business":
        return None  # unlimited

    return 0


def check_reminder_limit(db: Session, user):
    team = get_user_team(user)

    if not team:
        return False

    if team.plan not in ACTIVE_PLANS:
        return False

    limit = get_reminder_limit(team.plan)

    if limit is None:
        return True

    count = (
        db.query(Reminder)
        .join(Item, Reminder.item_id == Item.id)
        .filter(Item.team_id == team.id)
        .count()
    )

    return count < limit