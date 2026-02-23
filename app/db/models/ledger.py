import uuid
from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class LedgerEntry(Base):
    __tablename__ = "ledger"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    delta: Mapped[int] = mapped_column(Integer, nullable=False)  # +coins / -coins
    reason: Mapped[str] = mapped_column(String(64), nullable=False, default="manual")

    ref_type: Mapped[str | None] = mapped_column(String(32), nullable=True)  # payment|generation|admin
    ref_id: Mapped[str | None] = mapped_column(Text, nullable=True)

    actor: Mapped[str | None] = mapped_column(String(64), nullable=True)  # admin username / system

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
