from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_team
from ..models import ExternalContact, Team
from ..schemas import (
    ExternalContactCreate,
    ExternalContactRead,
    ExternalContactUpdate,
)

router = APIRouter()


@router.get("/", response_model=list[ExternalContactRead])
def list_external_contacts(
    db: Session = Depends(get_db),
    team: Team = Depends(get_current_team),
):
    return (
        db.query(ExternalContact)
        .filter(ExternalContact.team_id == team.id)
        .order_by(ExternalContact.company_name.asc())
        .all()
    )


@router.post(
    "/",
    response_model=ExternalContactRead,
    status_code=status.HTTP_201_CREATED,
)
def create_external_contact(
    payload: ExternalContactCreate,
    db: Session = Depends(get_db),
    team: Team = Depends(get_current_team),
):
    contact = ExternalContact(
        team_id=team.id,
        company_name=payload.company_name,
        contact_name=payload.contact_name,
        email=str(payload.email) if payload.email else None,
        phone=payload.phone,
        notes=payload.notes,
        active=payload.active,
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact


@router.get("/{contact_id}", response_model=ExternalContactRead)
def get_external_contact(
    contact_id: str,
    db: Session = Depends(get_db),
    team: Team = Depends(get_current_team),
):
    contact = (
        db.query(ExternalContact)
        .filter(
            ExternalContact.id == contact_id,
            ExternalContact.team_id == team.id,
        )
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="External contact not found.",
        )

    return contact


@router.put("/{contact_id}", response_model=ExternalContactRead)
def update_external_contact(
    contact_id: str,
    payload: ExternalContactUpdate,
    db: Session = Depends(get_db),
    team: Team = Depends(get_current_team),
):
    contact = (
        db.query(ExternalContact)
        .filter(
            ExternalContact.id == contact_id,
            ExternalContact.team_id == team.id,
        )
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="External contact not found.",
        )

    updates = payload.model_dump(exclude_unset=True)

    if "email" in updates and updates["email"] is not None:
        updates["email"] = str(updates["email"])

    for field, value in updates.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)

    return contact


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_external_contact(
    contact_id: str,
    db: Session = Depends(get_db),
    team: Team = Depends(get_current_team),
):
    contact = (
        db.query(ExternalContact)
        .filter(
            ExternalContact.id == contact_id,
            ExternalContact.team_id == team.id,
        )
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="External contact not found.",
        )

    db.delete(contact)
    db.commit()

    return None