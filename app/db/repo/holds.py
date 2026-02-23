from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.wallet_hold import WalletHold
from app.db.models.wallet import Wallet


async def get_held_amount(db: AsyncSession, user_id) -> int:
    res = await db.execute(
        select(func.coalesce(func.sum(WalletHold.amount), 0)).where(
            WalletHold.user_id == user_id,
            WalletHold.status == "held",
        )
    )
    return int(res.scalar_one())


async def create_hold(db: AsyncSession, user_id, amount: int, reason: str = "image_generation") -> WalletHold:
    hold = WalletHold(user_id=user_id, amount=int(amount), status="held", reason=reason)
    db.add(hold)
    await db.flush()
    return hold


async def finalize_hold(db: AsyncSession, hold_id) -> None:
    hold = (await db.execute(select(WalletHold).where(WalletHold.id == hold_id))).scalar_one()
    if hold.status != "held":
        return

    wallet = (await db.execute(select(Wallet).where(Wallet.user_id == hold.user_id))).scalar_one()
    wallet.balance -= int(hold.amount)

    hold.status = "finalized"
    hold.finalized_at = datetime.now(timezone.utc)


async def release_hold(db: AsyncSession, hold_id) -> None:
    hold = (await db.execute(select(WalletHold).where(WalletHold.id == hold_id))).scalar_one()
    if hold.status != "held":
        return
    hold.status = "released"
    hold.finalized_at = datetime.now(timezone.utc)