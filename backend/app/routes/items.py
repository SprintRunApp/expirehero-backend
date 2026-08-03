
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user, get_current_team
from ..models import (
    Item,
    UserProfile,
    Team,
    WorkflowGroup,
    Reminder,
    WorkflowCompletion,
    ExternalContact,
)
from ..schemas import (
    ItemCreate,
    ItemRead,
    ItemUpdate,
    WorkflowCompletionRead,
    WorkflowCompleteRequest,
)
from ..services.team_access import item_access_filter
from ..services.team_limits import has_active_plan
from calendar import monthrange
from datetime import date, datetime
from typing import Literal

router = APIRouter()


def add_months(source_date: date, months: int) -> date:
    if months <= 0:
        return source_date

    target_month_index = source_date.month - 1 + months
    target_year = source_date.year + target_month_index // 12
    target_month = target_month_index % 12 + 1

    target_day = min(
        source_date.day,
        monthrange(target_year, target_month)[1],
    )

    return date(
        year=target_year,
        month=target_month,
        day=target_day,
    )

def validate_workflow_group(
    workflow_group_id: str | None,
    team: Team,
    db: Session,
) -> None:
    if workflow_group_id is None:
        return

    group = (
        db.query(WorkflowGroup)
        .filter(
            WorkflowGroup.id == workflow_group_id,
            WorkflowGroup.team_id == team.id,
        )
        .first()
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow group does not belong to this team.",
        )


def validate_external_contact(
    external_contact_id: str | None,
    team: Team,
    db: Session,
) -> None:
    if external_contact_id is None:
        return

    contact = (
        db.query(ExternalContact)
        .filter(
            ExternalContact.id == external_contact_id,
            ExternalContact.team_id == team.id,
            ExternalContact.active.is_(True),
        )
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="External contact does not belong to this team or is inactive.",
        )
    
def get_accessible_item_or_404(
    item_id: str,
    db: Session,
    current_user: UserProfile,
) -> Item:
    item = (
        db.query(Item)
        .filter(
            Item.id == item_id,
            item_access_filter(current_user),
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found.",
        )

    return item

def ensure_item_can_be_edited(
    item: Item,
    current_user: UserProfile,
    team: Team,
) -> None:
    is_item_owner = item.owner_id == current_user.id
    is_team_owner = team.owner_id == current_user.id

    is_group_manager = (
        item.workflow_group is not None
        and item.workflow_group.manager_user_id == current_user.id
    )

    if is_item_owner or is_team_owner or is_group_manager:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to edit this workflow.",
    )

def ensure_item_can_be_deleted(
    item: Item,
    current_user: UserProfile,
    team: Team,
) -> None:
    is_item_owner = item.owner_id == current_user.id
    is_team_owner = team.owner_id == current_user.id

    if is_item_owner or is_team_owner:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to delete this workflow.",
    )


@router.get("/", response_model=list[ItemRead])
def list_items(
    workflow_status: Literal[
        "active",
        "completed",
        "cancelled",
    ] | None = None,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    query = (
        db.query(Item)
        .filter(item_access_filter(current_user))
    )

    if workflow_status is not None:
        query = query.filter(
            Item.status == workflow_status
        )

    if workflow_status == "completed":
        query = query.order_by(
            Item.completed_at.desc(),
            Item.created_at.desc(),
        )
    else:
        query = query.order_by(
            Item.created_at.desc()
        )

    return query.all()


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
    team: Team = Depends(get_current_team)
):
    team_id = team.id

    if not has_active_plan(team):
        raise HTTPException(
            status_code=403,
            detail="Active subscription required."
        )
    
    if payload.workflow_group_id and payload.visibility != "team":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A workflow assigned to a group must have team visibility.",
        )
    
    validate_workflow_group(
        workflow_group_id=payload.workflow_group_id,
        team=team,
        db=db,
    )

    validate_external_contact(
        external_contact_id=payload.external_contact_id,
        team=team,
        db=db,
    )

    if payload.external_email_enabled and not payload.external_contact_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="External email automation requires an external contact.",
        )

    item = Item(
        owner_id=current_user.id,
        title=payload.title,
        category=payload.category,
        notes=payload.notes,
        attachment_url=payload.attachment_url,
        visibility=payload.visibility,
        team_id=team_id if payload.visibility == "team" else None,
        workflow_group_id=payload.workflow_group_id,
        assigned_user_id=payload.assigned_user_id,
        notify_all=payload.notify_all,
        external_contact_id=payload.external_contact_id,
        external_email_enabled=payload.external_email_enabled,
        external_email_template=payload.external_email_template,
    )

    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.post(
    "/{item_id}/complete",
    response_model=ItemRead,
)
def complete_item(
    item_id: str,
    payload: WorkflowCompleteRequest,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
    team: Team = Depends(get_current_team),
):
    item = get_accessible_item_or_404(
        item_id=item_id,
        db=db,
        current_user=current_user,
    )

    ensure_item_can_be_edited(
        item=item,
        current_user=current_user,
        team=team,
    )

    if item.status == "completed":
        return item

    if item.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A cancelled workflow must be reopened "
                "before it can be completed."
            ),
        )

    reminder = (
        db.query(Reminder)
        .filter(
            Reminder.item_id == item.id,
            Reminder.status == "active",
        )
        .order_by(Reminder.created_at.desc())
        .first()
    )

    completed_at = datetime.utcnow()
    previous_due_date = reminder.due_date if reminder else None
    next_due_date = None

    if reminder and reminder.recurrence_months > 0:
        next_due_date = add_months(
            source_date=reminder.due_date,
            months=reminder.recurrence_months,
        )

    completion = WorkflowCompletion(
        item_id=item.id,
        reminder_id=reminder.id if reminder else None,
        completed_by_user_id=current_user.id,
        previous_due_date=previous_due_date,
        next_due_date=next_due_date,
        completed_at=completed_at,
        notes=payload.notes,
    )

    db.add(completion)

    if reminder and reminder.recurrence_months > 0:
        reminder.due_date = next_due_date
        reminder.status = "active"

        item.status = "active"
        item.completed_at = None

    else:
        if reminder:
            reminder.status = "completed"

        item.status = "completed"
        item.completed_at = completed_at

    db.commit()
    db.refresh(item)

    return item


@router.post(
    "/{item_id}/reopen",
    response_model=ItemRead,
)
def reopen_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
    team: Team = Depends(get_current_team),
):
    item = get_accessible_item_or_404(
        item_id=item_id,
        db=db,
        current_user=current_user,
    )

    ensure_item_can_be_edited(
        item=item,
        current_user=current_user,
        team=team,
    )

    if item.status == "active":
        return item

    item.status = "active"
    item.completed_at = None

    reminder = (
        db.query(Reminder)
        .filter(
            Reminder.item_id == item.id,
        )
        .order_by(Reminder.created_at.desc())
        .first()
    )

    if reminder:
        reminder.status = "active"

    db.commit()
    db.refresh(item)

    return item


@router.post(
    "/{item_id}/cancel",
    response_model=ItemRead,
)
def cancel_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
    team: Team = Depends(get_current_team),
):
    item = get_accessible_item_or_404(
        item_id=item_id,
        db=db,
        current_user=current_user,
    )

    ensure_item_can_be_edited(
        item=item,
        current_user=current_user,
        team=team,
    )

    if item.status == "cancelled":
        return item

    item.status = "cancelled"
    item.completed_at = None

    db.commit()
    db.refresh(item)

    return item

@router.get(
    "/{item_id}/completions",
    response_model=list[WorkflowCompletionRead],
)
def get_item_completions(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    item = get_accessible_item_or_404(
        item_id=item_id,
        db=db,
        current_user=current_user,
    )

    completions = (
        db.query(WorkflowCompletion)
        .filter(
            WorkflowCompletion.item_id == item.id,
        )
        .order_by(
            WorkflowCompletion.completed_at.desc(),
        )
        .all()
    )

    return [
        WorkflowCompletionRead(
            id=completion.id,
            item_id=completion.item_id,
            reminder_id=completion.reminder_id,
            completed_by_user_id=completion.completed_by_user_id,
            completed_by_name=(
                completion.completed_by.name
                if completion.completed_by
                else None
            ),
            completed_by_email=(
                completion.completed_by.email
                if completion.completed_by
                else None
            ),
            previous_due_date=completion.previous_due_date,
            next_due_date=completion.next_due_date,
            completed_at=completion.completed_at,
            notes=completion.notes,
        )
        for completion in completions
    ]

@router.get("/{item_id}", response_model=ItemRead)
def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    return get_accessible_item_or_404(
        item_id=item_id,
        db=db,
        current_user=current_user,
    )


@router.put("/{item_id}", response_model=ItemRead)
def update_item(
    item_id: str,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
    team: Team = Depends(get_current_team)
):
    item = get_accessible_item_or_404(
        item_id=item_id,
        db=db,
        current_user=current_user,
    )

    ensure_item_can_be_edited(
        item=item,
        current_user=current_user,
        team=team,
    )

    updates = payload.model_dump(exclude_unset=True)

    if "status" in updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Workflow status cannot be changed through the regular update endpoint. "
                "Use complete, reopen, or cancel."
            ),
        )

    if "completed_at" in updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="completed_at is managed automatically.",
        )

    if "workflow_group_id" in updates:
        validate_workflow_group(
            workflow_group_id=updates["workflow_group_id"],
            team=team,
            db=db,
        )

    if "external_contact_id" in updates:
        validate_external_contact(
            external_contact_id=updates["external_contact_id"],
            team=team,
            db=db,
        )

    new_external_contact_id = updates.get(
        "external_contact_id",
        item.external_contact_id,
    )

    new_external_email_enabled = updates.get(
        "external_email_enabled",
        item.external_email_enabled,
    )

    if new_external_email_enabled and not new_external_contact_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="External email automation requires an external contact.",
        )

    new_group_id = updates.get("workflow_group_id", item.workflow_group_id)
    new_visibility = updates.get("visibility", item.visibility)

    if new_group_id and new_visibility != "team":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A workflow assigned to a group must have team visibility.",
        )
    
    if "visibility" in updates:
        if updates["visibility"] == "team":
            updates["team_id"] = team.id
        else:
            updates["team_id"] = None

    for field, value in updates.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
    team: Team = Depends(get_current_team),
):
    item = get_accessible_item_or_404(
        item_id=item_id,
        db=db,
        current_user=current_user,
    )

    ensure_item_can_be_deleted(
        item=item,
        current_user=current_user,
        team=team,
    )

    db.delete(item)
    db.commit()

    return None