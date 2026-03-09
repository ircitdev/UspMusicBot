from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from loguru import logger

from database.crud import get_or_create_user
from config import settings


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_factory() as session:
            data["session"] = session
            return await handler(event, data)


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session = data.get("session")
        if not session:
            return await handler(event, data)

        tg_user = None
        if hasattr(event, "from_user") and event.from_user:
            tg_user = event.from_user

        if tg_user:
            try:
                user, created = await get_or_create_user(
                    session=session,
                    telegram_id=tg_user.id,
                    username=tg_user.username,
                    first_name=tg_user.first_name,
                    last_name=tg_user.last_name,
                    language_code=tg_user.language_code or "ru",
                    free_credits=settings.free_credits_on_start,
                )

                if user.is_blocked:
                    logger.warning(f"Blocked user {tg_user.id} tried to interact")
                    return

                data["user"] = user
                data["is_new_user"] = created

                if created:
                    logger.info(f"New user registered: {tg_user.id} @{tg_user.username}")
            except Exception as e:
                logger.error(f"UserMiddleware error: {e}")
                return await handler(event, data)

        return await handler(event, data)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        try:
            if isinstance(event, Message):
                user = event.from_user
                logger.debug(f"Message from {user.id} @{user.username}: {event.text or event.content_type}")
            elif isinstance(event, CallbackQuery):
                user = event.from_user
                logger.debug(f"Callback from {user.id}: {event.data}")
        except Exception:
            pass

        return await handler(event, data)
