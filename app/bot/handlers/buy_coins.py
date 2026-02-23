import uuid
from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery

from app.bot.keyboards.buy_coins import buy_coins_kb
from app.common.constants import COIN_PACKS

router = Router()

@router.message(F.text == "💳 Купить монеты")
async def buy_menu(message: Message):
    await message.answer("Выбери пакет монет:", reply_markup=buy_coins_kb())

@router.callback_query(F.data.startswith("buy:"))
async def buy_pack(call: CallbackQuery):
    pack_key = call.data.split("buy:", 1)[1]
    pack = COIN_PACKS.get(pack_key)
    if not pack:
        await call.answer("Пакет не найден", show_alert=True)
        return

    payload = f"{pack_key}:{uuid.uuid4().hex}"
    prices = [LabeledPrice(label=pack["title"], amount=int(pack["stars"]))]

    await call.message.bot.send_invoice(
        chat_id=call.message.chat.id,
        title=pack["title"],
        description=f"Пополнение баланса на {pack['coins']} монет",
        payload=payload,
        provider_token="",   # Stars
        currency="XTR",      # Stars currency
        prices=prices,
    )
    await call.answer()

@router.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment(message: Message, api):
    sp = message.successful_payment
    payload = sp.invoice_payload  # pack_key:uuid
    pack_key = payload.split(":", 1)[0]
    pack = COIN_PACKS.get(pack_key)
    if not pack:
        await message.answer("Оплата прошла, но пакет не распознан. Напиши в поддержку.")
        return

    res = await api.confirm_payment(
        telegram_id=message.from_user.id,
        invoice_payload=payload,
        telegram_payment_charge_id=sp.telegram_payment_charge_id,
    )

    if res["already_processed"]:
        await message.answer(f"ℹ️ Платёж уже был учтён ранее.\n🪙 Баланс: {res['new_balance']}")
    else:
        await message.answer(f"✅ Оплата прошла! Монеты начислены.\n🪙 Новый баланс: {res['new_balance']}")


    
