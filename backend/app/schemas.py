from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserMe(BaseModel):
    id: UUID
    firebase_uid: str
    email: EmailStr
    name: str | None = None
    plan: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=64)
    notes: str | None = None
    attachment_url: str | None = None
    visibility: str = "private"

    assigned_user_id: Optional[str] = None
    notify_all: bool = False


class ItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    category: str | None = Field(default=None, min_length=1, max_length=64)
    notes: str | None = None
    attachment_url: str | None = None
    archived: bool | None = None

    assigned_user_id: Optional[str] = None
    notify_all: Optional[bool] = None


class ItemRead(BaseModel):
    id: UUID
    title: str
    category: str
    notes: str | None = None
    attachment_url: str | None = None
    archived: bool
    created_at: datetime
    visibility: str
    team_id: int | None = None

    assigned_user_id: Optional[str] = None
    notify_all: bool

    created_at: datetime

class Config:
    from_attributes = True

   


class ReminderCreate(BaseModel):
    item_id: UUID
    due_date: date
    timezone: str = "UTC"
    recurrence_months: int = 0
    advance_days: list[int] = [30, 7, 0]


class ReminderUpdate(BaseModel):
    due_date: date | None = None
    recurrence_months: int | None = None
    advance_days: list[int] | None = None
    status: str | None = None


class ReminderRead(BaseModel):
    id: UUID
    item_id: UUID
    due_date: date
    timezone: str
    recurrence_months: int
    advance_days: list[int]
    status: str
    created_at: datetime
    ui_status: str
    days_left: int

    model_config = {"from_attributes": True}


class ReminderWithItem(BaseModel):
    id: UUID
    item_id: UUID
    due_date: date
    timezone: str
    recurrence_months: int
    advance_days: list[int]
    status: str
    created_at: datetime
    ui_status: str
    days_left: int
    item_title: str
    item_category: str

    email_status: str | None = None
    last_email_sent_at: datetime | None = None
    email_sent_count: int = 0


from pydantic import BaseModel


class TeamCreate(BaseModel):
    name: str


class TeamRead(BaseModel):
    id: int
    name: str
    owner_id: str

    class Config:
        from_attributes = True

class AddTeamMember(BaseModel):
    email: str


class TeamMemberRead(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True



class NotificationRead(BaseModel):
    id: UUID
    recipient_email: str
    channel: str
    trigger_days: int
    due_date: date
    scheduled_at: datetime
    sent_at: datetime | None = None
    status: str
    error: str | None = None

    model_config = {"from_attributes": True}


class TeamInviteCreate(BaseModel):
    email: EmailStr
    role: str = "employee"


class TeamInviteRead(BaseModel):
    id: int
    email: EmailStr
    role: str
    accepted: bool
    expires_at: datetime

    model_config = {"from_attributes": True}


class InviteInfo(BaseModel):
    email: EmailStr
    role: str
    team_name: str
    expires_at: datetime