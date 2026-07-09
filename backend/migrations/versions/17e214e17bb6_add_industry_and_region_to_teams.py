"""add industry and region to teams

Revision ID: 17e214e17bb6
Revises: a4d9389d41f5
Create Date: 2026-07-09 12:37:07.545179

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17e214e17bb6'
down_revision: Union[str, Sequence[str], None] = 'a4d9389d41f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "teams",
        sa.Column("industry", sa.String(length=64), nullable=True)
    )
    op.add_column(
        "teams",
        sa.Column("region", sa.String(length=16), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("teams", "region")
    op.drop_column("teams", "industry")
