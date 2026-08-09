"""add country to teams

Revision ID: 2251990fd70a
Revises: 83307e851e5e
Create Date: 2026-08-09 17:30:12.587843

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2251990fd70a'
down_revision: Union[str, Sequence[str], None] = '83307e851e5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "teams",
        sa.Column(
            "country",
            sa.String(length=16),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "teams",
        "country",
    )



