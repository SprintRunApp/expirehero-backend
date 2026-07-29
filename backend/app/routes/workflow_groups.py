from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_team
from ..models import WorkflowGroup, Team
from ..schemas import WorkflowGroupCreate, WorkflowGroupRead

router = APIRouter()


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