"""add project column

Revision ID: 488d221b8280
Revises: d5421a5cd5bb
Create Date: 2025-03-20 11:05:22.813736

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "488d221b8280"
down_revision: Union[str, None] = "d5421a5cd5bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "old_shorten_links", sa.Column("project", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "shorten_links", sa.Column("project", sa.String(length=255), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("shorten_links", "project")
    op.drop_column("old_shorten_links", "project")
