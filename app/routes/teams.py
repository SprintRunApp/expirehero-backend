from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user
from ..models import Team, UserProfile

from ..schemas import TeamCreate, TeamRead, AddTeamMember, TeamMemberRead

router = APIRouter()


@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(
    payload: TeamCreate,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    # ❌ user już ma team?
    if current_user.owned_team or current_user.team_membership:
        raise HTTPException(
            status_code=400,
            detail="User already in a team"
        )

    team = Team(
        name=payload.name,
        owner_id=current_user.id
    )

    db.add(team)
    db.commit()
    db.refresh(team)

    return team


@router.get("/me", response_model=TeamRead | None)
def get_my_team(
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    # owner
    if current_user.owned_team:
        return current_user.owned_team

    # member
    if current_user.team_membership:
        return current_user.team_membership.team

    return None

from ..models import TeamMember, UserProfile

@router.post("/add-member", status_code=201)
def add_member(
    payload: AddTeamMember,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    # 🔒 tylko owner może dodawać
    if not current_user.owned_team:
        raise HTTPException(status_code=403, detail="Not a team owner")

    team = current_user.owned_team

    # 🔍 znajdź usera po emailu
    user = db.query(UserProfile).filter(UserProfile.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ❌ user już w teamie?
    if user.team_membership:
        raise HTTPException(status_code=400, detail="User already in a team")

    # ❌ nie dodawaj siebie
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot add yourself")

    member = TeamMember(
        team_id=team.id,
        user_id=user.id,
        role="member"
    )

    db.add(member)
    db.commit()

    return {"message": "User added to team"}

@router.get("/members", response_model=list[TeamMemberRead])
def list_members(
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    # owner
    if current_user.owned_team:
        team = current_user.owned_team

    # member
    elif current_user.team_membership:
        team = current_user.team_membership.team

    else:
        raise HTTPException(status_code=404, detail="No team")

    members = db.query(TeamMember).filter(TeamMember.team_id == team.id).all()

    result = []

    for m in members:
        result.append(
            TeamMemberRead(
                id=m.id,
                email=m.user.email,
                role=m.role
            )
        )

    return result