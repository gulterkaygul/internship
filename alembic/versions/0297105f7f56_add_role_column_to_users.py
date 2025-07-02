"""Add role column to users

Revision ID: 0297105f7f56
Revises: 0a7f9d994125
Create Date: 2025-07-01 12:28:04.768993

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0297105f7f56'
down_revision: Union[str, Sequence[str], None] = '0a7f9d994125'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('users', sa.Column('role', sa.String(), nullable=True))
    op.execute("UPDATE users SET role = 'user' WHERE role IS NULL")
    op.alter_column('users', 'role', nullable=False)


def downgrade():
    op.drop_column('users', 'role')
