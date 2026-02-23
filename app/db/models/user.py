import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)

    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(64), nullable=True)

    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")  # user|support|admin
    is_banned: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    wallet: Mapped["Wallet"] = relationship(back_populates="user", uselist=False)  # type: ignore[name-defined]
    payments: Mapped[list["Payment"]] = relationship(back_populates="user")  # type: ignore[name-defined]