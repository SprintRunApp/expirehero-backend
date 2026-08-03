from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user, get_current_team
from ..models import (
    UserProfile,
    Team,
    WorkflowGroup,
    Item,
    Reminder,
)
from ..schemas import IndustryTemplateApply
from ..services.industry_templates import INDUSTRY_TEMPLATES
from ..services.team_limits import has_active_plan


router = APIRouter()


@router.get("/{industry}")
def get_industry_template(industry: str):
    template = INDUSTRY_TEMPLATES.get(industry)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Industry template not found.",
        )

    return template


@router.post("/{industry}/apply")
def apply_industry_template(
    industry: str,
    payload: IndustryTemplateApply,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
    team: Team = Depends(get_current_team),
):
    template = INDUSTRY_TEMPLATES.get(industry)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Industry template not found.",
        )

    if not has_active_plan(team):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active subscription required.",
        )

    created_groups = {}
    created_items = []
    created_reminders = []

    try:
        for selection in payload.workflows:

            # -----------------------------------
            # 1. Find group in template
            # -----------------------------------

            template_group = next(
                (
                    group
                    for group in template["groups"]
                    if group["name"] == selection.group_name
                ),
                None,
            )

            if not template_group:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Template group "
                        f"'{selection.group_name}' not found."
                    ),
                )

            # -----------------------------------
            # 2. Find workflow in template group
            # -----------------------------------

            template_workflow = next(
                (
                    workflow
                    for workflow in template_group["workflows"]
                    if workflow["title"] == selection.workflow_title
                ),
                None,
            )

            if not template_workflow:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Workflow "
                        f"'{selection.workflow_title}' "
                        f"not found in group "
                        f"'{selection.group_name}'."
                    ),
                )

            # -----------------------------------
            # 3. Create/reuse WorkflowGroup
            # -----------------------------------

            group = created_groups.get(
                selection.group_name
            )

            if not group:
                group = (
                    db.query(WorkflowGroup)
                    .filter(
                        WorkflowGroup.team_id == team.id,
                        WorkflowGroup.name == selection.group_name,
                    )
                    .first()
                )

                if not group:
                    group = WorkflowGroup(
                        team_id=team.id,
                        name=template_group["name"],
                        description=template_group.get(
                            "description"
                        ),
                        manager_user_id=current_user.id,
                        active=True,
                    )

                    db.add(group)
                    db.flush()

                created_groups[
                    selection.group_name
                ] = group

            # -----------------------------------
            # 4. Create real editable Item
            # -----------------------------------

            item = Item(
                owner_id=current_user.id,
                title=template_workflow["title"],
                category=template_workflow["category"],
                visibility="team",
                team_id=team.id,
                workflow_group_id=group.id,
                assigned_user_id=None,
                notify_all=False,
                archived=False,
                status="active",
            )

            db.add(item)
            db.flush()

            # -----------------------------------
            # 5. Create real editable Reminder
            # -----------------------------------

            reminder = Reminder(
                item_id=item.id,
                due_date=selection.due_date,
                timezone="UTC",
                recurrence_months=template_workflow.get(
                    "recurrence_months",
                    0,
                ),
                advance_days=template_workflow.get(
                    "advance_days",
                    [30, 14, 7, 3, 1],
                ),
                status="active",
            )

            db.add(reminder)
            db.flush()

            created_items.append(item)
            created_reminders.append(reminder)

        # -----------------------------------
        # 6. Save everything together
        # -----------------------------------

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "status": "created",
        "industry": industry,
        "groups_created_or_used": len(created_groups),
        "workflows_created": len(created_items),
        "reminders_created": len(created_reminders),
        "workflows": [
            {
                "id": item.id,
                "title": item.title,
                "category": item.category,
                "workflow_group_id": item.workflow_group_id,
                "status": item.status,
                "reminder": {
                    "id": reminder.id,
                    "due_date": reminder.due_date,
                    "recurrence_months": reminder.recurrence_months,
                    "advance_days": reminder.advance_days,
                },
            }
            for item, reminder in zip(
                created_items,
                created_reminders,
            )
        ],
    }