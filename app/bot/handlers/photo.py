from __future__ import annotations

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, BufferedInputFile

from app.bot.handlers.menu import BTN_PHOTO

import httpx
from urllib.parse import urlparse

router = Router()


class PhotoGen(StatesGroup):
    waiting_prompt = State()


@router.message(F.text == BTN_PHOTO)
async def photo_start(message: Message, state: FSMContext):
    await state.set_state(PhotoGen.waiting_prompt)
    await message.answer("🖼 Напиши промпт для генерации фото (спишется 10 монет).")


def _extract_http_error(exc: Exception) -> tuple[int | None, str]:
    """
    Достаём HTTP status + body из исключения максимально надёжно:
    - httpx.HTTPStatusError (имеет .response)
    - обёрнутые исключения (внутри __cause__/__context__)
    - fallback по строке
    """
    # 1) Прямой httpx error
    if isinstance(exc, httpx.HTTPStatusError) and exc.response is not None:
        return exc.response.status_code, (exc.response.text or "")

    # 2) Часто ошибка спрятана в cause/context
    for inner in (getattr(exc, "__cause__", None), getattr(exc, "__context__", None)):
        if isinstance(inner, httpx.HTTPStatusError) and inner.response is not None:
            return inner.response.status_code, (inner.response.text or "")

    # 3) Иногда ApiClient делает "raise RuntimeError(str(e))" — ловим по тексту
    msg = str(exc)
    if "402" in msg and "Payment Required" in msg:
        return 402, msg
    if "401" in msg and "Unauthorized" in msg:
        return 401, msg
    if "500" in msg and "Internal Server Error" in msg:
        return 500, msg

    return None, msg


@router.message(PhotoGen.waiting_prompt)
async def photo_prompt(message: Message, state: FSMContext, api):
    prompt = (message.text or "").strip()
    if len(prompt) < 3:
        await message.answer("Слишком коротко. Напиши промпт чуть подробнее.")
        return

    await message.answer("⏳ Генерирую...")

    try:
        # 1) Генерация (может выбросить исключение при 402/401/500)
        res = await api.generate_photo(telegram_id=message.from_user.id, prompt=prompt)

        # 2) Скачиваем картинку ВНУТРИ docker-сети и отправляем байтами
        img_url = res.get("image_url") or ""
        if not img_url:
            await message.answer("❌ API вернул пустой image_url.")
            return

        # абсолютный -> берём path, относительный -> как есть
        if img_url.startswith("http://") or img_url.startswith("https://"):
            path = urlparse(img_url).path
        else:
            path = img_url

        if not path.startswith("/"):
            path = "/" + path

        # Важно: для скачивания используем внутренний base_url (обычно http://api:8000)
        base = getattr(api, "base_url", "http://api:8000").rstrip("/")
        internal_url = f"{base}{path}"

        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.get(internal_url)
            r.raise_for_status()
            image_bytes = r.content

        photo = BufferedInputFile(image_bytes, filename="generated.png")

        spent = res.get("spent", 0)
        new_balance = res.get("new_balance", "?")

        await message.answer_photo(
            photo=photo,
            caption=f"✅ Готово! Списано {spent} монет.\n🪙 Баланс: {new_balance}",
        )

    except Exception as e:
        status, body = _extract_http_error(e)

        if status == 402:
            await message.answer("❌ Недостаточно монет для генерации фото. Пополни баланс в меню.")
        elif status == 401:
            await message.answer("❌ Ошибка доступа к API (401). Проверь internal key.")
        elif status is not None:
            # Покажем аккуратный кусок ответа
            snippet = (body or "")[:300]
            await message.answer(f"❌ Ошибка API: {status}\n{snippet}")
        else:
            await message.answer(f"❌ Ошибка: {type(e).__name__}: {e}")

    finally:
        await state.clear()