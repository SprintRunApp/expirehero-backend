from sqlalchemy.orm import Session

from ..models import Item, UserProfile, Team
from .protection_engine import ProtectionStage


def add_recipient(
    recipients: dict[str, UserProfile],
    user: UserProfile | None,
) -> None:
    if not user:
        return

    if not user.email:
        return

    recipients[str(user.id)] = user


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

    if not team:
        return None

    return team.owner


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
        add_recipient(
            recipients,
            membership.user,
        )

    return list(recipients.values())


def get_recipients(
    item: Item,
    db: Session,
    stage: ProtectionStage,
) -> list[UserProfile]:
    recipients: dict[str, UserProfile] = {}

    company_owner = get_team_owner(
        item=item,
        db=db,
    )

    # 1. Osoba bezpośrednio odpowiedzialna
    if item.assigned_user:
        add_recipient(
            recipients,
            item.assigned_user,
        )
    else:
        # Brak przypisanej osoby:
        # owner przejmuje odpowiedzialność od początku.
        add_recipient(
            recipients,
            company_owner,
        )

    # 2. Finalna eskalacja
    # Owner = manager firmy.
    if stage.severity in {"urgent", "critical"}:
        add_recipient(
            recipients,
            company_owner,
        )

    # 3. Jawne notify_all nadal respektujemy
    if item.notify_all and item.team_id:
        for user in get_all_team_members(
            team_id=item.team_id,
            db=db,
        ):
            add_recipient(
                recipients,
                user,
            )

    return list(recipients.values())