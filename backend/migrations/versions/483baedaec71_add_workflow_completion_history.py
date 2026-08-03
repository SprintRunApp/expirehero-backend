"""add workflow completion history

Revision ID: 483baedaec71
Revises: caa3d2d73389
Create Date: 2026-08-03 17:26:08.965522

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '483baedaec71'
down_revision: Union[str, Sequence[str], None] = 'caa3d2d73389'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workflow_completions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("item_id", sa.String(length=36), nullable=False),
        sa.Column("reminder_id", sa.String(length=36), nullable=True),
        sa.Column(
            "completed_by_user_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column("previous_due_date", sa.Date(), nullable=True),
        sa.Column("next_due_date", sa.Date(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["completed_by_user_id"],
            ["user_profiles.id"],
        ),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["items.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["reminder_id"],
            ["reminders.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_workflow_completions_item_id"),
        "workflow_completions",
        ["item_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_workflow_completions_reminder_id"),
        "workflow_completions",
        ["reminder_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_workflow_completions_completed_by_user_id"),
        "workflow_completions",
        ["completed_by_user_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_workflow_completions_completed_at"),
        "workflow_completions",
        ["completed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_workflow_completions_completed_at"),
        table_name="workflow_completions",
    )

    op.drop_index(
        op.f("ix_workflow_completions_completed_by_user_id"),
        table_name="workflow_completions",
    )

    op.drop_index(
        op.f("ix_workflow_completions_reminder_id"),
        table_name="workflow_completions",
    )

    op.drop_index(
        op.f("ix_workflow_completions_item_id"),
        table_name="workflow_completions",
    )

    op.drop_table("workflow_completions")
