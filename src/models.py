from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, DateTime, String, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from fastapi_users.db import SQLAlchemyBaseUserTableUUID

Base: DeclarativeMeta = declarative_base()


class User(SQLAlchemyBaseUserTableUUID, Base):
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )


class ShortenLink(Base):
    __tablename__ = "shorten_links"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    shorten_link: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    user_id: Mapped[Optional[str]] = mapped_column( 
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )
    clicks: Mapped[int] = mapped_column(default=0)

    last_clicked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )


class OldShortenLink(Base):
    __tablename__ = "old_shorten_links"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    shorten_link: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )
    clicks: Mapped[int] = mapped_column(nullable=True)

    last_clicked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    deleted_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
