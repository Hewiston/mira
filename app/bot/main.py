import asyncio
from aiogram import Bot, Dispatcher

from app.common.config import settings
from app.common.logging import setup_logging
from app.bot.services.api_client import ApiClient
from app.bot.middlewares.api import ApiMiddleware

from app.bot.handlers.menu import router as menu_router
from app.bot.handlers.buy_coins import router as buy_router
from app.bot.handlers.menu import BTN_PHOTO
from app.bot.handlers.photo import router as photo_router

setup_logging()


async def main():
    dp = Dispatcher()

    api = ApiClient(base_url=f"http://localhost:{settings.api_port}", internal_api_key=settings.internal_api_key)
    dp.update.middleware(ApiMiddleware(api))

    dp.include_router(menu_router)
    dp.include_router(buy_router)
    dp.include_router(photo_router)


    async with Bot(token=settings.bot_token) as bot:
        await dp.start_polling(bot)


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()
