from __future__ import annotations
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, date


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

    assigned_user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("user_profiles.id"),
        nullable=True
    )
    notify_all: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    team: Mapped["Team | None"] = relationship("Team")
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
    recurrence_months: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    advance_days: Mapped[list[int]] = mapped_column(JSON, default=[30, 7, 0], nullable=False)
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


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    owner_id = Column(String, ForeignKey("user_profiles.id"), nullable=False, unique=True)

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