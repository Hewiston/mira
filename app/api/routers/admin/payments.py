from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.db.models.payment import Payment

router = APIRouter(prefix="/v1/admin/payments", tags=["admin-payments"])


class PaymentRow(BaseModel):
    id: str
    user_id: str
    provider: str
    status: str
    currency: str
    stars_amount: int
    coins_amount: int
    charge_id: str | None
    created_at: str
    paid_at: str | None


class PaymentsOut(BaseModel):
    items: list[PaymentRow]


@router.get("", response_model=PaymentsOut)
async def list_payments(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    q = select(Payment)
    if status:
        q = q.where(Payment.status == status)
    res = await db.execute(q.order_by(Payment.created_at.desc()).limit(200))
    items=[]
    for p in res.scalars().all():
        items.append(PaymentRow(
            id=str(p.id),
            user_id=str(p.user_id),
            provider=p.provider,
            status=p.status,
            currency=p.currency,
            stars_amount=int(p.stars_amount),
            coins_amount=int(p.coins_amount),
            charge_id=p.telegram_payment_charge_id,
            created_at=p.created_at.isoformat(),
            paid_at=p.paid_at.isoformat() if p.paid_at else None,
        ))
    return PaymentsOut(items=items)


@router.get("/{payment_id}", response_model=PaymentRow)
async def get_payment(
    payment_id: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    pid = UUID(payment_id)
    p = (await db.execute(select(Payment).where(Payment.id == pid))).scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    return PaymentRow(
        id=str(p.id),
        user_id=str(p.user_id),
        provider=p.provider,
        status=p.status,
        currency=p.currency,
        stars_amount=int(p.stars_amount),
        coins_amount=int(p.coins_amount),
        charge_id=p.telegram_payment_charge_id,
        created_at=p.created_at.isoformat(),
        paid_at=p.paid_at.isoformat() if p.paid_at else None,
    )
