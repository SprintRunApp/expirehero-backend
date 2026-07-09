from ..models import Team


def get_user_limit(plan: str):

    if plan == "starter":
        return 3

    if plan == "pro":
        return 10

    if plan == "business":
        return None

    return 0


def can_add_member(team: Team):

    limit = get_user_limit(team.plan)

    if limit is None:
        return True

    current_users = len(team.members) + 1  # owner

    return current_users < limit

ACTIVE_PLANS = ["starter", "pro", "business"]


def has_active_plan(team):
    if not team:
        return False

    return team.plan in ACTIVE_PLANS