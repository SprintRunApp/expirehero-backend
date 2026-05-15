
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from ..deps import get_current_user
from ..models import Item, Reminder, UserProfile
from ..schemas import ReminderCreate, ReminderRead, ReminderUpdate, ReminderWithItem
from ..services.reminder_status import compute_days_left, compute_ui_status
from ..services.plan_limits import check_reminder_limit
from ..services.team_access import item_access_filter

router = APIRouter()


@router.get("/", response_model=list[ReminderWithItem])
def list_reminders(
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    reminders = (
        db.query(Reminder)
        .options(joinedload(Reminder.item))
        .join(Item, Reminder.item_id == Item.id)
        .filter(item_access_filter(current_user))
        .order_by(Reminder.due_date.asc())
        .all()
    )

    result: list[ReminderWithItem] = []

    for reminder in reminders:
        result.append(
            ReminderWithItem(
                id=reminder.id,
                item_id=reminder.item_id,
                due_date=reminder.due_date,
                recurrence_months=reminder.recurrence_months,
                advance_days=reminder.advance_days,
                status=reminder.status,
                created_at=reminder.created_at,
                ui_status=compute_ui_status(reminder.due_date),
                days_left=compute_days_left(reminder.due_date),
                item_title=reminder.item.title,
                item_category=reminder.item.category,
            )
        )

    return result


@router.post("/", response_model=ReminderRead, status_code=status.HTTP_201_CREATED)
def create_reminder(
    payload: ReminderCreate,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    
    if not check_reminder_limit(db, current_user):
        raise HTTPException(
            status_code=403,
            detail="Free plan limit reached. Upgrade to PRO."
        )

    item_id = str(payload.item_id)

    item = (
    db.query(Item)
        .filter(
            Item.id == item_id,
            item_access_filter(current_user)
        )
        .first()
)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    reminder = Reminder(
        item_id=item_id,
        due_date=payload.due_date,
        recurrence_months=payload.recurrence_months,
        advance_days=payload.advance_days,
        status="active",
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return ReminderRead(
        id=reminder.id,
        item_id=reminder.item_id,
        due_date=reminder.due_date,
        recurrence_months=reminder.recurrence_months,
        advance_days=reminder.advance_days,
        status=reminder.status,
        created_at=reminder.created_at,
        ui_status=compute_ui_status(reminder.due_date),
        days_left=compute_days_left(reminder.due_date),
    )


@router.get("/{reminder_id}", response_model=ReminderRead)
def get_reminder(
    reminder_id: str,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    reminder = (
        db.query(Reminder)
        .join(Item, Reminder.item_id == Item.id)
        .filter(Reminder.id == reminder_id, Item.owner_id == current_user.id)
        .first()
    )

    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    return ReminderRead(
        id=reminder.id,
        item_id=reminder.item_id,
        due_date=reminder.due_date,
        recurrence_months=reminder.recurrence_months,
        advance_days=reminder.advance_days,
        status=reminder.status,
        created_at=reminder.created_at,
        ui_status=compute_ui_status(reminder.due_date),
        days_left=compute_days_left(reminder.due_date),
    )


@router.put("/{reminder_id}", response_model=ReminderRead)
def update_reminder(
    reminder_id: str,
    payload: ReminderUpdate,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    reminder = (
        db.query(Reminder)
        .join(Item, Reminder.item_id == Item.id)
        .filter(Reminder.id == reminder_id, Item.owner_id == current_user.id)
        .first()
    )

    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    updates = payload.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(reminder, field, value)

    db.commit()
    db.refresh(reminder)

    return ReminderRead(
        id=reminder.id,
        item_id=reminder.item_id,
        due_date=reminder.due_date,
        recurrence_months=reminder.recurrence_months,
        advance_days=reminder.advance_days,
        status=reminder.status,
        created_at=reminder.created_at,
        ui_status=compute_ui_status(reminder.due_date),
        days_left=compute_days_left(reminder.due_date),
    )


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(
    reminder_id: str,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    reminder = (
        db.query(Reminder)
        .join(Item, Reminder.item_id == Item.id)
        .filter(
            Reminder.id == reminder_id,
            item_access_filter(current_user)
        )
        .first()
    )

    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    db.delete(reminder)
    db.commit()
    return None

