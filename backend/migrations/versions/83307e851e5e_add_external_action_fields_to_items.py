"""add external action fields to items

Revision ID: 83307e851e5e
Revises: 483baedaec71
Create Date: 2026-08-03 19:31:38.329548

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83307e851e5e'
down_revision: Union[str, Sequence[str], None] = '483baedaec71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "items",
        sa.Column(
            "external_contact_id",
            sa.String(length=36),
            nullable=True,
        ),
    )

    op.add_column(
        "items",
        sa.Column(
            "external_email_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "items",
        sa.Column(
            "external_email_template",
            sa.Text(),
            nullable=True,
        ),
    )

    op.create_index(
        op.f("ix_items_external_contact_id"),
        "items",
        ["external_contact_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_items_external_contact_id",
        "items",
        "external_contacts",
        ["external_contact_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.alter_column(
        "items",
        "external_email_enabled",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_items_external_contact_id",
        "items",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_items_external_contact_id"),
        table_name="items",
    )

    op.drop_column(
        "items",
        "external_email_template",
    )

    op.drop_column(
        "items",
        "external_email_enabled",
    )

    op.drop_column(
        "items",
        "external_contact_id",
    )
