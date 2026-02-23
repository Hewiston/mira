from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.common.constants import COIN_PACKS


def buy_coins_kb() -> InlineKeyboardMarkup:
    buttons = []
    for key, pack in COIN_PACKS.items():
        buttons.append([InlineKeyboardButton(text=f"{pack['title']} — ⭐{pack['stars']}", callback_data=f"buy:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)