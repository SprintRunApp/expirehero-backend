"""add assigned_user

Revision ID: 39a1f5854596
Revises: 
Create Date: 2026-04-11 13:50:40.637409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39a1f5854596'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'items',
        sa.Column('assigned_user_id', sa.String(length=36), nullable=True)
    )

    op.add_column(
        'items',
        sa.Column('notify_all', sa.Boolean(), nullable=False, server_default=sa.false())
    )

    op.create_foreign_key(
        'fk_items_assigned_user_id',
        'items',
        'user_profiles',
        ['assigned_user_id'],
        ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_items_assigned_user_id', 'items', type_='foreignkey')
    op.drop_column('items', 'notify_all')
    op.drop_column('items', 'assigned_user_id')


