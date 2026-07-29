from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_team
from ..models import WorkflowGroup, Team, TeamMember
from ..schemas import (
    WorkflowGroupCreate,
    WorkflowGroupRead,
    WorkflowGroupUpdate,
)

router = APIRouter()


def validate_manager(
    manager_user_id: str | None,
    team: Team,
    db: Session,
) -> None:
    """
    Sprawdza, czy wybrany manager należy do danego zespołu.

    Managerem może być:
    - właściciel zespołu,
    - członek zespołu.
    """

    if manager_user_id is None:
        return

    if manager_user_id == team.owner_id:
        return

    membership = (
        db.query(TeamMember)
        .filter(
            TeamMember.team_id == team.id,
            TeamMember.user_id == manager_user_id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected manager does not belong to this team.",
        )


@router.get("/", response_model=list[WorkflowGroupRead])
def list_workflow_groups(
    db: Session = Depends(get_db),
    team: Team = Depends(get_current_team),
):
    return (
        db.query(WorkflowGroup)
        .filter(WorkflowGroup.team_id == team.id)
        .order_by(WorkflowGroup.name.asc())
        .all()
    )


@router.post(
    "/",
    response_model=WorkflowGroupRead,
    status_code=status.HTTP_201_CREATED,
)
def create_workflow_group(
    payload: WorkflowGroupCreate,
    db: Session = Depends(get_db),
    team: Team = Depends(get_current_team),
):
    validate_manager(
        manager_user_id=payload.manager_user_id,
        team=team,
        db=db,
    )

    group = WorkflowGroup(
        team_id=team.id,
        name=payload.name,
        description=payload.description,
        manager_user_id=payload.manager_user_id,
        active=payload.active,
    )

    db.add(group)
    db.commit()
    db.refresh(group)

    return group


@router.get("/{group_id}", response_model=WorkflowGroupRead)
def get_workflow_group(
    group_id: str,
    db: Session = Depends(get_db),
    team: Team = Depends(get_current_team),
):
    group = (
        db.query(WorkflowGroup)
        .filter(
            WorkflowGroup.id == group_id,
            WorkflowGroup.team_id == team.id,
        )
        .first()
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow group not found.",
        )

    return group


@router.put("/{group_id}", response_model=WorkflowGroupRead)
def update_workflow_group(
    group_id: str,
    payload: WorkflowGroupUpdate,
    db: Session = Depends(get_db),
    team: Team = Depends(get_current_team),
):
    group = (
        db.query(WorkflowGroup)
        .filter(
            WorkflowGroup.id == group_id,
            WorkflowGroup.team_id == team.id,
        )
        .first()
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow group not found.",
        )

    updates = payload.model_dump(exclude_unset=True)

    if "manager_user_id" in updates:
        validate_manager(
            manager_user_id=updates["manager_user_id"],
            team=team,
            db=db,
        )

    for field, value in updates.items():
        setattr(group, field, value)

    db.commit()
    db.refresh(group)

    return group


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_workflow_group(
    group_id: str,
    db: Session = Depends(get_db),
    team: Team = Depends(get_current_team),
):
    group = (
        db.query(WorkflowGroup)
        .filter(
            WorkflowGroup.id == group_id,
            WorkflowGroup.team_id == team.id,
        )
        .first()
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow group not found.",
        )

    db.delete(group)
    db.commit()

    return None