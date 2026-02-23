import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.db.models.user import User
from app.db.models.wallet import Wallet
from app.db.models.ledger import LedgerEntry
from app.db.models.admin_audit_log import AdminAuditLog

router = APIRouter(prefix="/v1/admin/users", tags=["admin-users"])


class UserRow(BaseModel):
    id: str
    telegram_id: int
    username: str | None
    first_name: str | None
    role: str
    is_banned: bool
    balance: int


class UsersOut(BaseModel):
    items: list[UserRow]


@router.get("", response_model=UsersOut)
async def list_users(
    search: str | None = None,
    role: str | None = None,
    banned: bool | None = None,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_admin),
):
    q = select(User, Wallet).join(Wallet, Wallet.user_id == User.id)
    if search:
        s = search.strip()
        # telegram_id search if digits
        conds = []
        if s.isdigit():
            conds.append(User.telegram_id == int(s))
        conds.append(User.username.ilike(f"%{s}%"))
        conds.append(User.first_name.ilike(f"%{s}%"))
        q = q.where(or_(*conds))
    if role:
        q = q.where(User.role == role)
    if banned is not None:
        q = q.where(User.is_banned == banned)

    res = await db.execute(q.order_by(User.created_at.desc()).limit(200))
    items = []
    for user, wallet in res.all():
        items.append(UserRow(
            id=str(user.id),
            telegram_id=int(user.telegram_id),
            username=user.username,
            first_name=user.first_name,
            role=user.role,
            is_banned=bool(user.is_banned),
            balance=int(wallet.balance),
        ))
    return UsersOut(items=items)


class UserDetailOut(BaseModel):
    id: str
    telegram_id: int
    username: str | None
    first_name: str | None
    role: str
    is_banned: bool
    balance: int


@router.get("/{user_id}", response_model=UserDetailOut)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    try:
        uid = UUID(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Bad user_id")
    res = await db.execute(
        select(User, Wallet).join(Wallet, Wallet.user_id == User.id).where(User.id == uid)
    )
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    user, wallet = row
    return UserDetailOut(
        id=str(user.id),
        telegram_id=int(user.telegram_id),
        username=user.username,
        first_name=user.first_name,
        role=user.role,
        is_banned=bool(user.is_banned),
        balance=int(wallet.balance),
    )


class RoleIn(BaseModel):
    role: str = Field(pattern="^(user|support|admin)$")


@router.post("/{user_id}/role")
async def set_role(
    user_id: str,
    payload: RoleIn,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_admin),
):
    uid = UUID(user_id)
    user = (await db.execute(select(User).where(User.id == uid))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    user.role = payload.role
    db.add(AdminAuditLog(actor=admin["sub"], action="user.role", target=str(uid), meta=json.dumps({"role": payload.role})))
    await db.commit()
    return {"ok": True}


@router.post("/{user_id}/ban")
async def ban_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_admin),
):
    uid = UUID(user_id)
    user = (await db.execute(select(User).where(User.id == uid))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    user.is_banned = True
    db.add(AdminAuditLog(actor=admin["sub"], action="user.ban", target=str(uid), meta=None))
    await db.commit()
    return {"ok": True}


@router.post("/{user_id}/unban")
async def unban_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_admin),
):
    uid = UUID(user_id)
    user = (await db.execute(select(User).where(User.id == uid))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    user.is_banned = False
    db.add(AdminAuditLog(actor=admin["sub"], action="user.unban", target=str(uid), meta=None))
    await db.commit()
    return {"ok": True}


class CreditsAdjustIn(BaseModel):
    delta: int = Field(ge=-1_000_000, le=1_000_000)
    reason: str = Field(min_length=1, max_length=64, default="manual")


@router.post("/{user_id}/credits/adjust")
async def adjust_credits(
    user_id: str,
    payload: CreditsAdjustIn,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_admin),
):
    uid = UUID(user_id)
    wallet = (await db.execute(select(Wallet).where(Wallet.user_id == uid))).scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    wallet.balance = int(wallet.balance) + int(payload.delta)

    db.add(LedgerEntry(
        user_id=uid,
        delta=int(payload.delta),
        reason=payload.reason,
        ref_type="admin",
        ref_id=str(uid),
        actor=admin["sub"],
    ))
    db.add(AdminAuditLog(actor=admin["sub"], action="credits.adjust", target=str(uid), meta=json.dumps({"delta": payload.delta, "reason": payload.reason})))
    await db.commit()
    return {"ok": True, "new_balance": int(wallet.balance)}
