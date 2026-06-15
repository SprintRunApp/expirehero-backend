from datetime import datetime, timedelta
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user
from ..models import Team, TeamMember, UserProfile, TeamInvite
from ..schemas import (
    TeamCreate,
    TeamRead,
    AddTeamMember,
    TeamMemberRead,
    TeamInviteCreate,
    TeamInviteRead,
    InviteInfo,
)
from app.services.email_service import email_service

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

@router.delete("/members/{member_id}")
def remove_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    team = db.query(Team).filter(Team.owner_id == current_user.id).first()

    if not team:
        raise HTTPException(
            status_code=403,
            detail="Only team owner can remove members"
        )

    member = (
        db.query(TeamMember)
        .filter(
            TeamMember.id == member_id,
            TeamMember.team_id == team.id
        )
        .first()
    )

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Owner cannot remove themselves"
        )

    db.delete(member)
    db.commit()

    return {"message": "Member removed"}

@router.post("/invite", response_model=TeamInviteRead)
def invite_team_member(

    
    payload: TeamInviteCreate,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    
    print("📨 INVITE PAYLOAD:", payload)
    print("👤 CURRENT USER:", current_user.email)


    team = db.query(Team).filter(Team.owner_id == current_user.id).first()

    if not team:
        raise HTTPException(
            status_code=403,
            detail="Only team owner can send invitations"
        )

    if payload.role not in ["manager", "employee"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    existing_member = (
        db.query(UserProfile)
        .join(TeamMember, TeamMember.user_id == UserProfile.id)
        .filter(
            TeamMember.team_id == team.id,
            UserProfile.email == payload.email
        )
        .first()
    )

    if existing_member:
        raise HTTPException(status_code=400, detail="User is already in team")

    token = secrets.token_urlsafe(32)

    invite = TeamInvite(
        team_id=team.id,
        email=payload.email,
        role=payload.role,
        name=payload.name,
        token=token,
        invited_by_id=current_user.id,
        expires_at=datetime.utcnow() + timedelta(days=7),
        accepted=False,
    )

    db.add(invite)
    db.commit()
    db.refresh(invite)

    invite_url = f"https://www.expireheros.app/invite/{token}"

    print("📧 SENDING INVITE EMAIL TO:", payload.email)

    email_service.send_email(
        to_email=payload.email,
        subject="You were invited to ExpireHero",
        content=f"""Hello,

You have been invited to join a team in ExpireHero.

Role: {payload.role}

Accept invitation:
{invite_url}

This invitation expires in 7 days.

– ExpireHero
"""
    )

    print("✅ INVITE CREATED:", invite.id, invite.email, invite.name)

    return invite


@router.get("/invites", response_model=list[TeamInviteRead])
def list_team_invites(
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    team = db.query(Team).filter(Team.owner_id == current_user.id).first()

    if not team:
        raise HTTPException(
            status_code=403,
            detail="Only team owner can send invitations"
        )

    invites = (
        db.query(TeamInvite)
        .filter(TeamInvite.team_id == team.id)
        .order_by(TeamInvite.created_at.desc())
        .all()
    )

    return invites


@router.delete("/invite/{invite_id}")
def cancel_invite(
    invite_id: int,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    team = db.query(Team).filter(Team.owner_id == current_user.id).first()

    if not team:
        raise HTTPException(
            status_code=403,
            detail="Only team owner can cancel invitations"
        )

    invite = (
        db.query(TeamInvite)
        .filter(
            TeamInvite.id == invite_id,
            TeamInvite.team_id == team.id
        )
        .first()
    )

    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    if invite.accepted:
        raise HTTPException(
            status_code=400,
            detail="Accepted invitation cannot be cancelled"
        )

    db.delete(invite)
    db.commit()

    return {"message": "Invitation cancelled"}

@router.get("/invite/{token}", response_model=InviteInfo)
def get_invite_info(
    token: str,
    db: Session = Depends(get_db),
):
    invite = (
        db.query(TeamInvite)
        .filter(TeamInvite.token == token)
        .first()
    )

    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    if invite.accepted:
        raise HTTPException(status_code=400, detail="Invite already accepted")

    if invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invite expired")

    return InviteInfo(
        email=invite.email,
        role=invite.role,
        team_name=invite.team.name,
        expires_at=invite.expires_at,
        name=invite.name,
    )

@router.post("/invite/{token}/accept")
def accept_invite(
    token: str,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    invite = (
        db.query(TeamInvite)
        .filter(TeamInvite.token == token)
        .first()
    )

    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    if invite.accepted:
        raise HTTPException(status_code=400, detail="Invite already accepted")

    if invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invite expired")

    print("🔥 ACCEPT INVITE USER:", current_user.id, current_user.email)
    print("🔥 OWNED TEAM:", current_user.owned_team)
    print("🔥 TEAM MEMBERSHIP:", current_user.team_membership)

    # ❌ user already in team
    if current_user.owned_team or current_user.team_membership:
        raise HTTPException(
            status_code=400,
            detail="User already belongs to a team"
        )

    # ❌ invite email mismatch
    if current_user.email.lower() != invite.email.lower():
        raise HTTPException(
            status_code=403,
            detail="This invite belongs to another email"
        )

    member = TeamMember(
        team_id=invite.team_id,
        user_id=current_user.id,
        role=invite.role,
    )

    db.add(member)

    invite.accepted = True

    db.commit()

    return {
        "message": "Invite accepted"
    }