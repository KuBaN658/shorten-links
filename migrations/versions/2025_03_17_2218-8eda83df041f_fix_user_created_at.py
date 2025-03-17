"""fix user created_at

Revision ID: 8eda83df041f
Revises: 1af40832bae4
Create Date: 2025-03-17 22:18:40.157483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8eda83df041f'
down_revision: Union[str, None] = '1af40832bae4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('user', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user', 'created_at')
