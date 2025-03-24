"""In OldShortenLink set alias not unique

Revision ID: d449cd8d3801
Revises: 9f0f1ee6b530
Create Date: 2025-03-23 12:38:17.453189

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d449cd8d3801"
down_revision: Union[str, None] = "9f0f1ee6b530"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "old_shorten_links_alias_key", "old_shorten_links", type_="unique"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.create_unique_constraint(
        "old_shorten_links_alias_key", "old_shorten_links", ["alias"]
    )
