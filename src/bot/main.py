import asyncio
import sys
import os
import logging
import socket

# Добавляем src/ в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from config import settings
from database.engine import create_tables, async_session
from bot.middleware import DatabaseMiddleware, UserMiddleware, LoggingMiddleware
from handlers import setup_routers
from utils.logger import setup_logger


async def main():
    setup_logger(settings.log_level)
    logging.basicConfig(level=logging.INFO)

    logger.info("Starting UspMusicBot...")

    # Создаём таблицы БД
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    await create_tables()
    logger.info("Database tables created/verified")

    # FSM Storage
    storage = MemoryStorage()

    # Создаём bot с IPv4-only connector
    session = AiohttpSession()
    session._connector_init["family"] = socket.AF_INET
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
        session=session,
    )

    me = await bot.get_me()
    logger.info(f"Bot: @{me.username} ({me.first_name})")

    dp = Dispatcher(storage=storage)

    # Роутеры
    router = setup_routers()
    dp.include_router(router)

    # Middleware
    for observer in [dp.message, dp.callback_query]:
        observer.middleware(DatabaseMiddleware(async_session))
        observer.middleware(UserMiddleware())
        observer.middleware(LoggingMiddleware())

    # Добавляем обработчик update для дебага
    @dp.update.outer_middleware()
    async def log_update(handler, event, data):
        logger.info(f"Received update: {event.update_id}")
        return await handler(event, data)

    # Запуск
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot is starting polling...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
