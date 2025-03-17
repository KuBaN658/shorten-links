"""initial migration

Revision ID: 1af40832bae4
Revises: 
Create Date: 2025-03-17 22:14:40.143353

"""
from typing import Sequence, Union

from alembic import op
import fastapi_users_db_sqlalchemy
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1af40832bae4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('users_service',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('registered_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_service_id'), 'users_service', ['id'], unique=False)
    op.create_table('old_shorten_links',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('url', sa.Text(), nullable=False),
    sa.Column('shorten_link', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('clicks', sa.Integer(), nullable=True),
    sa.Column('last_clicked_at', sa.DateTime(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users_service.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('shorten_link')
    )
    op.create_table('shorten_links',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('url', sa.Text(), nullable=False),
    sa.Column('shorten_link', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('clicks', sa.Integer(), nullable=False),
    sa.Column('last_clicked_at', sa.DateTime(), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users_service.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('shorten_link')
    )
    op.create_table('user',
    sa.Column('id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('shorten_links')
    op.drop_table('old_shorten_links')
    op.drop_index(op.f('ix_users_service_id'), table_name='users_service')
    op.drop_table('users_service')
