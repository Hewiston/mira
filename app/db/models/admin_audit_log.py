import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class AdminAuditLog(Base):
    __tablename__ = "admin_audit_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    actor: Mapped[str] = mapped_column(String(64), nullable=False)  # admin username
    action: Mapped[str] = mapped_column(String(64), nullable=False)  # e.g. user.ban, credits.adjust
    target: Mapped[str | None] = mapped_column(String(64), nullable=True)  # e.g. user_id
    meta: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
