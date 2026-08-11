from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime
from datetime import datetime
from .database import Base


class TikTokAccount(Base):
    __tablename__ = "tiktok_accounts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    open_id: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    access_token: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    refresh_token: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    expires_in: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    refresh_expires_in: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    scope: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    token_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    access_token_expires_at: Mapped[datetime] = mapped_column(
    DateTime,
    nullable=False,
)