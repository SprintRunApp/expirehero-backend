from __future__ import annotations
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, date, timedelta


from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


# 🔥 helper: UUID jako string
def uuid_str():
    return str(uuid.uuid4())


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)

    firebase_uid: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    plan: Mapped[str] = mapped_column(String(32), default="free", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    items: Mapped[list["Item"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        foreign_keys="Item.owner_id"  # 🔥 KLUCZOWE
    )

    owned_team = relationship("Team", back_populates="owner", uselist=False)
    team_membership = relationship("TeamMember", back_populates="user", uselist=False)

class Item(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    owner_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user_profiles.id"),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachment_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    visibility: Mapped[str] = mapped_column(String(32), nullable=False, default="private")
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)

    workflow_group_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("workflow_groups.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    assigned_user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("user_profiles.id"),
        nullable=True
    )
    notify_all: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    status: Mapped[str] = mapped_column(
        String(32),
        default="active",
        nullable=False,
        index=True
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    team: Mapped["Team | None"] = relationship("Team")
    workflow_group: Mapped["WorkflowGroup | None"] = relationship(
        "WorkflowGroup",
        back_populates="items"
    )
    external_contact_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("external_contacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    external_email_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    external_email_template: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    owner: Mapped["UserProfile"] = relationship(
        back_populates="items",
        foreign_keys=[owner_id]
    )
    assigned_user: Mapped["UserProfile | None"] = relationship(
        "UserProfile",
        foreign_keys=[assigned_user_id]
    )

    reminders: Mapped[list["Reminder"]] = relationship(
        back_populates="item",
        cascade="all, delete-orphan"
    )

    completions: Mapped[list["WorkflowCompletion"]] = relationship(
        "WorkflowCompletion",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="WorkflowCompletion.completed_at.desc()",
    )

    external_contact: Mapped["ExternalContact | None"] = relationship(
        "ExternalContact",
        foreign_keys=[external_contact_id],
    )

class Reminder(Base):
    __tablename__ = "reminders"
    

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    recurrence_months: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    advance_days: Mapped[list[int]] = mapped_column(
        JSON,
        default=lambda: [30, 14, 7, 3, 1],
        nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    item: Mapped["Item"] = relationship(back_populates="reminders")
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="reminder",
        cascade="all, delete-orphan"
    )

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    reminder_id: Mapped[str] = mapped_column(String(36), ForeignKey("reminders.id", ondelete="CASCADE"), nullable=False, index=True)

    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    reminder: Mapped["Reminder"] = relationship(back_populates="notifications")

    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("user_profiles.id"), nullable=True)

    trigger_days: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)

class WorkflowCompletion(Base):
    __tablename__ = "workflow_completions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=uuid_str,
    )

    item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    reminder_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("reminders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    completed_by_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user_profiles.id"),
        nullable=False,
        index=True,
    )

    previous_due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    next_due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    completed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    item: Mapped["Item"] = relationship(
        "Item",
        back_populates="completions",
    )

    reminder: Mapped["Reminder | None"] = relationship(
        "Reminder",
    )

    completed_by: Mapped["UserProfile"] = relationship(
        "UserProfile",
        foreign_keys=[completed_by_user_id],
    )

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    owner_id = Column(String, ForeignKey("user_profiles.id"), nullable=False, unique=True)

    plan = Column(String(32), nullable=False, default="pending")
    industry = Column(String(64), nullable=True)
    region = Column(String(16), nullable=True)

    country = Column(String(16), nullable=True)

    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("UserProfile", back_populates="owned_team")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)

    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False, unique=True)
    
    role = Column(String, nullable=False, default="member")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team", back_populates="members")
    user = relationship("UserProfile", back_populates="team_membership")


class TeamInvite(Base):
    __tablename__ = "team_invites"

    id = Column(Integer, primary_key=True, index=True)

    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    email = Column(String, nullable=False, index=True)

    role = Column(String, nullable=False, default="employee")

    token = Column(String, nullable=False, unique=True, index=True)

    invited_by_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)

    accepted = Column(Boolean, nullable=False, default=False)

    name = Column(String, nullable=True)

    expires_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.utcnow() + timedelta(days=7)
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team")
    invited_by = relationship("UserProfile")

class WorkflowGroup(Base):
    __tablename__ = "workflow_groups"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=uuid_str
    )

    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    manager_user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("user_profiles.id"),
        nullable=True,
        index=True
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    team: Mapped["Team"] = relationship("Team")

    manager: Mapped["UserProfile | None"] = relationship(
        "UserProfile",
        foreign_keys=[manager_user_id]
    )

    items: Mapped[list["Item"]] = relationship(
        "Item",
        back_populates="workflow_group"
    )


class ExternalContact(Base):
    __tablename__ = "external_contacts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=uuid_str
    )

    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    contact_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )

    phone: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    team: Mapped["Team"] = relationship("Team")