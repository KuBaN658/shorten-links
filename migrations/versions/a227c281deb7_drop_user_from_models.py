"""drop user from models

Revision ID: a227c281deb7
Revises: 4fde316a88ed
Create Date: 2025-03-17 16:49:30.192700

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a227c281deb7"
down_revision: Union[str, None] = "4fde316a88ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index("ix_user_id", table_name="user")
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.drop_column("user", "registered_at")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "user",
        sa.Column(
            "registered_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
    )
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.create_index("ix_user_id", "user", ["id"], unique=False)
