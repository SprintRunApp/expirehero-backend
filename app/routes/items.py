from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user
from ..models import Item, UserProfile
from ..schemas import ItemCreate, ItemRead, ItemUpdate
from ..services.team_access import item_access_filter, get_user_team_id

router = APIRouter()


@router.get("/", response_model=list[ItemRead])
def list_items(
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    items = (
        db.query(Item)
        .filter(item_access_filter(current_user))
        .order_by(Item.created_at.desc())
        .all()
    )
    return items


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    team_id = get_user_team_id(current_user)

    item = Item(
        owner_id=current_user.id,
        title=payload.title,
        category=payload.category,
        notes=payload.notes,
        attachment_url=payload.attachment_url,
        visibility=payload.visibility if hasattr(payload, "visibility") else "private",
        team_id=team_id if getattr(payload, "visibility", "private") == "team" else None,
        assigned_user_id=payload.assigned_user_id,
        notify_all=payload.notify_all,
    )

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=ItemRead)
def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    item = (
        db.query(Item)
        .filter(Item.id == item_id, Item.owner_id == current_user.id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


@router.put("/{item_id}", response_model=ItemRead)
def update_item(
    item_id: str,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    item = (
        db.query(Item)
        .filter(Item.id == item_id, Item.owner_id == current_user.id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    updates = payload.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user)
):
    item = (
        db.query(Item)
        .filter(Item.id == item_id, Item.owner_id == current_user.id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return None