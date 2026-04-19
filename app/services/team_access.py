from sqlalchemy import or_, and_

from ..models import Item, UserProfile


def get_user_team_id(user: UserProfile):
    if user.owned_team:
        return user.owned_team.id

    if user.team_membership:
        return user.team_membership.team.id

    return None


def item_access_filter(user: UserProfile):
    team_id = get_user_team_id(user)

    # tylko prywatne
    if not team_id:
        return Item.owner_id == user.id

    # prywatne + teamowe
    return or_(
        Item.owner_id == user.id,
        and_(
            Item.visibility == "team",
            Item.team_id == team_id
        )
    )