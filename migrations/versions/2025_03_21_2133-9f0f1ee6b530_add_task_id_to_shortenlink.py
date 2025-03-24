"""add task_id to ShortenLink

Revision ID: 9f0f1ee6b530
Revises: 488d221b8280
Create Date: 2025-03-21 21:33:55.197666

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f0f1ee6b530"
down_revision: Union[str, None] = "488d221b8280"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "shorten_links", sa.Column("task_id", sa.String(length=255), nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("shorten_links", "task_id")
