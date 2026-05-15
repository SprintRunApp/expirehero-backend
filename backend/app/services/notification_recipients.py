from sqlalchemy.orm import Session

from ..models import Item, UserProfile, Team


def get_all_team_members(team_id: int, db: Session) -> list[UserProfile]:
    if not team_id:
        return []

    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return []

    recipients: list[UserProfile] = []

    if team.owner and team.owner.email:
        recipients.append(team.owner)

    for member in team.members:
        if member.user and member.user.email:
            recipients.append(member.user)

    unique = {}
    for user in recipients:
        unique[user.id] = user

    return list(unique.values())


def get_recipients(item: Item, db: Session) -> list[UserProfile]:
    recipients: list[UserProfile] = []

    if item.owner and item.owner.email:
        recipients.append(item.owner)

    if item.assigned_user_id and item.assigned_user and item.assigned_user.email:
        recipients.append(item.assigned_user)

    elif item.notify_all and item.team_id:
        recipients.extend(get_all_team_members(item.team_id, db))

    unique = {}
    for user in recipients:
        unique[user.id] = user

    return list(unique.values())