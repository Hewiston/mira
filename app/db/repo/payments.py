from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.payment import Payment


async def get_payment_by_charge_id(db: AsyncSession, charge_id: str) -> Payment | None:
    res = await db.execute(
        select(Payment).where(Payment.telegram_payment_charge_id == charge_id)
    )
    return res.scalar_one_or_none()


async def create_payment(
    db: AsyncSession,
    user_id,
    invoice_payload: str,
    charge_id: str,
    coins_amount: int,
    stars_amount: int,
    currency: str = "XTR",
    provider: str = "telegram_stars",
) -> Payment:
    payment = Payment(
        user_id=user_id,
        provider=provider,
        invoice_payload=invoice_payload,
        stars_amount=int(stars_amount),
        coins_amount=int(coins_amount),
        currency=currency,
        status="paid",
        telegram_payment_charge_id=charge_id,
        paid_at=datetime.now(timezone.utc),
    )
    db.add(payment)
    return payment