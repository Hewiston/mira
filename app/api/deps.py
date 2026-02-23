import secrets
from collections.abc import AsyncGenerator
from fastapi import Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.config import settings
from app.db.models.base import SessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def require_internal_api_key(
    x_internal_key: str | None = Header(default=None, alias="X-Internal-Key"),
) -> None:
    if not settings.internal_api_key:
        return

    if not x_internal_key or not secrets.compare_digest(x_internal_key, settings.internal_api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal API key")

from fastapi import Header
from app.common.config import settings
from app.api.auth.admin_tokens import verify_token


async def require_admin(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing admin token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = verify_token(settings.admin_token_secret, token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid admin token")
    if payload.get("role") not in ("admin", "support"):
        raise HTTPException(status_code=403, detail="Forbidden")
    return payload
