from sqlalchemy.orm import Session

from ..models import Item, UserProfile, Team
from .protection_engine import ProtectionStage


def add_recipient(
    recipients: dict,
    user: UserProfile | None,
) -> None:
    if not user:
        return

    if not user.email:
        return

    recipients[str(user.id)] = user


def get_all_team_members(
    team_id: int,
    db: Session,
) -> list[UserProfile]:
    team = (
        db.query(Team)
        .filter(Team.id == team_id)
        .first()
    )

    if not team:
        return []

    recipients: dict[str, UserProfile] = {}

    add_recipient(recipients, team.owner)

    for membership in team.members:
        add_recipient(recipients, membership.user)

    return list(recipients.values())


def get_workflow_manager(
    item: Item,
    db: Session,
) -> UserProfile | None:
    workflow_group = getattr(item, "workflow_group", None)

    if not workflow_group:
        return None

    manager_user_id = workflow_group.manager_user_id

    if not manager_user_id:
        return None

    return (
        db.query(UserProfile)
        .filter(UserProfile.id == manager_user_id)
        .first()
    )


def get_team_owner(
    item: Item,
    db: Session,
) -> UserProfile | None:
    if not item.team_id:
        return None

    team = (
        db.query(Team)
        .filter(Team.id == item.team_id)
        .first()
    )

    return team.owner if team else None


def get_recipients(
    item: Item,
    db: Session,
    stage: ProtectionStage,
) -> list[UserProfile]:
    """
    Eskalacja odbiorców:

    Zawsze:
    - twórca workflow,
    - osoba przypisana.

    Od drugiego poziomu:
    - manager grupy workflow.

    Na dwóch ostatnich poziomach:
    - właściciel firmy.

    notify_all:
    - wszyscy członkowie zespołu.
    """
    recipients: dict[str, UserProfile] = {}

    add_recipient(recipients, item.owner)
    add_recipient(recipients, item.assigned_user)

    if stage.level >= 2:
        manager = get_workflow_manager(item, db)
        add_recipient(recipients, manager)

    if stage.severity in {"urgent", "critical"}:
        team_owner = get_team_owner(item, db)
        add_recipient(recipients, team_owner)

    if item.notify_all and item.team_id:
        for user in get_all_team_members(item.team_id, db):
            add_recipient(recipients, user)

    return list(recipients.values())