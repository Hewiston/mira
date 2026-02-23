from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

router = Router()

BTN_BALANCE = "🪙 Баланс"
BTN_BUY = "💳 Купить монеты"
BTN_PHOTO = "🖼 Фото"
BTN_VIDEO = "🎬 Видео"
BTN_MY = "📂 Мои генерации"

def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_BALANCE), KeyboardButton(text=BTN_BUY)],
            [KeyboardButton(text=BTN_PHOTO), KeyboardButton(text=BTN_VIDEO)],
            [KeyboardButton(text=BTN_MY)],
        ],
        resize_keyboard=True,
    )

@router.message(CommandStart())
async def start(message: Message, api):
    data = await api.ensure_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )
    await message.answer(
        f"👋 Привет! Аккаунт готов.\n🪙 Баланс: {data['balance']} монет",
        reply_markup=main_menu(),
    )

@router.message(F.text == BTN_BALANCE)
async def balance(message: Message, api):
    data = await api.get_wallet(telegram_id=message.from_user.id)
    await message.answer(f"🪙 Твой баланс: {data['balance']} монет")