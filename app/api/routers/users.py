from fastapi import APIRouter, Depends, HTTPException

from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_internal_api_key
from app.db.repo.users import ensure_user, add_coins, get_or_create_wallet_by_telegram_id
from app.db.repo.payments import get_payment_by_charge_id, create_payment
from app.common.constants import COIN_PACKS

router = APIRouter(prefix="/v1", tags=["users"])


class EnsureUserIn(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None


class EnsureUserOut(BaseModel):
    user_id: str
    balance: int


@router.post("/users/ensure", response_model=EnsureUserOut)
async def ensure_user_route(payload: EnsureUserIn, db: AsyncSession = Depends(get_db)):
    user, wallet = await ensure_user(
        db,
        telegram_id=payload.telegram_id,
        username=payload.username,
        first_name=payload.first_name,
    )
    await db.commit()
    return EnsureUserOut(user_id=str(user.id), balance=int(wallet.balance))


class WalletOut(BaseModel):
    balance: int


@router.get("/wallet/{telegram_id}", response_model=WalletOut)
async def wallet_route(telegram_id: int, db: AsyncSession = Depends(get_db)):
    wallet = await get_or_create_wallet_by_telegram_id(db, telegram_id=telegram_id)
    return WalletOut(balance=int(wallet.balance))


class TopupIn(BaseModel):
    telegram_id: int
    coins: int = Field(gt=0)
    reason: str | None = None
    payment_id: str | None = None


class TopupOut(BaseModel):
    balance: int


@router.post("/wallet/topup", response_model=TopupOut)
async def wallet_topup_route(
    payload: TopupIn,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_internal_api_key),
):
    new_balance = await add_coins(db, telegram_id=payload.telegram_id, coins=payload.coins)
    await db.commit()
    return TopupOut(balance=int(new_balance))


class ConfirmPaymentIn(BaseModel):
    telegram_id: int
    telegram_payment_charge_id: str
    invoice_payload: str


class ConfirmPaymentOut(BaseModel):
    new_balance: int
    already_processed: bool


@router.post("/payments/confirm", response_model=ConfirmPaymentOut)
async def confirm_payment_route(
    payload: ConfirmPaymentIn,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_internal_api_key),
):
    charge_id = payload.telegram_payment_charge_id

    existing = await get_payment_by_charge_id(db, charge_id=charge_id)
    if existing:
        wallet = await get_or_create_wallet_by_telegram_id(db, telegram_id=payload.telegram_id)
        return ConfirmPaymentOut(new_balance=int(wallet.balance), already_processed=True)

    pack_key = payload.invoice_payload.split(":", 1)[0]
    pack = COIN_PACKS.get(pack_key)
    if not pack:
        raise HTTPException(status_code=400, detail="Unknown coin pack in invoice_payload")

    try:
        wallet = await get_or_create_wallet_by_telegram_id(db, telegram_id=payload.telegram_id)

        await create_payment(
            db,
            user_id=wallet.user_id,
            invoice_payload=payload.invoice_payload,
            charge_id=charge_id,
            coins_amount=int(pack["coins"]),
            stars_amount=int(pack["stars"]),
            currency="XTR",
        )

        new_balance = await add_coins(db, telegram_id=payload.telegram_id, coins=int(pack["coins"]))

        await db.commit()
        return ConfirmPaymentOut(new_balance=int(new_balance), already_processed=False)

    except IntegrityError:
        await db.rollback()
        wallet = await get_or_create_wallet_by_telegram_id(db, telegram_id=payload.telegram_id)
        return ConfirmPaymentOut(new_balance=int(wallet.balance), already_processed=True)

    except Exception:
        await db.rollback()
        raise
