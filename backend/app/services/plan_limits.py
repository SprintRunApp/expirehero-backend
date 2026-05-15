from sqlalchemy.orm import Session

from ..models import Reminder, Item
from ..config import settings


def check_reminder_limit(db: Session, user):

    if user.plan == "pro":
        return True

    count = (
        db.query(Reminder)
        .join(Item, Reminder.item_id == Item.id)
        .filter(Item.owner_id == user.id)
        .count()
    )

    if count >= settings.FREE_REMINDER_LIMIT:
        return False

    return True