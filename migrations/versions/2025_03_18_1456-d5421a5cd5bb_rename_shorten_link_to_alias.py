"""rename shorten_link to alias

Revision ID: d5421a5cd5bb
Revises: 9c2283d2c179
Create Date: 2025-03-18 14:56:38.760218

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d5421a5cd5bb"
down_revision: Union[str, None] = "9c2283d2c179"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "old_shorten_links", sa.Column("alias", sa.String(length=255), nullable=False)
    )
    op.drop_constraint(
        "old_shorten_links_shorten_link_key", "old_shorten_links", type_="unique"
    )
    op.create_unique_constraint(None, "old_shorten_links", ["alias"])
    op.drop_column("old_shorten_links", "shorten_link")
    op.add_column(
        "shorten_links", sa.Column("alias", sa.String(length=255), nullable=False)
    )
    op.drop_constraint(
        "shorten_links_shorten_link_key", "shorten_links", type_="unique"
    )
    op.create_unique_constraint(None, "shorten_links", ["alias"])
    op.drop_column("shorten_links", "shorten_link")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "shorten_links",
        sa.Column(
            "shorten_link", sa.VARCHAR(length=255), autoincrement=False, nullable=False
        ),
    )
    op.drop_constraint(None, "shorten_links", type_="unique")
    op.create_unique_constraint(
        "shorten_links_shorten_link_key", "shorten_links", ["shorten_link"]
    )
    op.drop_column("shorten_links", "alias")
    op.add_column(
        "old_shorten_links",
        sa.Column(
            "shorten_link", sa.VARCHAR(length=255), autoincrement=False, nullable=False
        ),
    )
    op.drop_constraint(None, "old_shorten_links", type_="unique")
    op.create_unique_constraint(
        "old_shorten_links_shorten_link_key", "old_shorten_links", ["shorten_link"]
    )
    op.drop_column("old_shorten_links", "alias")
