"""add workflow status to items

Revision ID: caa3d2d73389
Revises: 287a79f591c5
Create Date: 2026-07-29 16:40:46.186717
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "caa3d2d73389"
down_revision: Union[str, Sequence[str], None] = "287a79f591c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "items",
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default="active",
        ),
    )

    op.add_column(
        "items",
        sa.Column(
            "completed_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.create_index(
        op.f("ix_items_status"),
        "items",
        ["status"],
        unique=False,
    )

    op.alter_column(
        "items",
        "status",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_items_status"),
        table_name="items",
    )

    op.drop_column("items", "completed_at")
    op.drop_column("items", "status")