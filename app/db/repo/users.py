from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.db.models.wallet import Wallet


async def add_coins(session: AsyncSession, telegram_id: int, coins: int) -> int:
    # 1) user по telegram_id
    res_u = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = res_u.scalar_one_or_none()
    if not user:
        # если у тебя пользователь всегда должен существовать — можно raise
        user = User(telegram_id=telegram_id)
        session.add(user)
        await session.flush()  # чтобы получить user.id

    # 2) wallet по user.id (UUID)
    res_w = await session.execute(select(Wallet).where(Wallet.user_id == user.id))
    wallet = res_w.scalar_one_or_none()
    if not wallet:
        wallet = Wallet(user_id=user.id, balance=0)
        session.add(wallet)
        await session.flush()

    # 3) начисляем
    wallet.balance += int(coins)

    await session.commit()
    await session.refresh(wallet)
    return wallet.balance


async def ensure_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    first_name: str | None,
) -> tuple[User, Wallet]:
    q = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = q.scalar_one_or_none()

    if user is None:
        user = User(telegram_id=telegram_id, username=username, first_name=first_name)
        session.add(user)
        await session.flush()  # чтобы появился user.id

        wallet = Wallet(user_id=user.id, balance=0)
        session.add(wallet)
        await session.flush()
    else:
        # обновим имя/юзернейм, если изменились
        if username and user.username != username:
            user.username = username
        if first_name and user.first_name != first_name:
            user.first_name = first_name

        q2 = await session.execute(select(Wallet).where(Wallet.user_id == user.id))
        wallet = q2.scalar_one()
    return user, wallet


async def get_or_create_wallet_by_telegram_id(session: AsyncSession, telegram_id: int) -> Wallet:
    # 1) ищем юзера
    q = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = q.scalar_one_or_none()

    # 2) если нет — создаём
    if user is None:
        user = User(telegram_id=telegram_id)
        session.add(user)
        await session.flush()  # получаем user.id

        wallet = Wallet(user_id=user.id, balance=0)
        session.add(wallet)
        await session.flush()
        return wallet

    # 3) ищем кошелёк
    q2 = await session.execute(select(Wallet).where(Wallet.user_id == user.id))
    wallet = q2.scalar_one_or_none()

    # 4) если нет — создаём
    if wallet is None:
        wallet = Wallet(user_id=user.id, balance=0)
        session.add(wallet)
        await session.flush()

    return wallet
