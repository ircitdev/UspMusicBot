from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func
from loguru import logger

from bot.keyboards import Keyboards
from bot.states import AdminStates
from bot.texts import ADMIN_STATS
from database.models import User, Song, Transaction, AnalyticsDaily
from database.crud import get_user_by_telegram_id, update_user_balance, block_user
from config import settings

router = Router()


def is_admin(user: User) -> bool:
    return user.is_admin or user.telegram_id in settings.admin_ids


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery, session, user: User):
    if not is_admin(user):
        await callback.answer("⛔ Нет доступа")
        return

    total_users = (await session.execute(select(func.count()).select_from(User))).scalar()
    total_songs = (await session.execute(select(func.count()).select_from(Song))).scalar()

    from datetime import date
    today = date.today()
    today_result = await session.execute(
        select(AnalyticsDaily).where(AnalyticsDaily.date == today)
    )
    today_data = today_result.scalar_one_or_none()

    text = ADMIN_STATS.format(
        total_users=total_users,
        total_songs=total_songs,
        revenue_today=f"{today_data.revenue_rub:.0f}" if today_data else "0",
        new_users=today_data.new_users if today_data else 0,
        active_users=today_data.active_users if today_data else 0,
        songs_today=today_data.songs_generated if today_data else 0,
    )

    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=Keyboards.admin_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext, user: User):
    if not is_admin(user):
        await callback.answer("⛔ Нет доступа")
        return
    await state.set_state(AdminStates.waiting_for_broadcast_message)
    await callback.message.edit_text(
        "📢 *Рассылка*\n\nОтправь сообщение для рассылки всем пользователям.\n\n"
        "Поддерживается Markdown разметка.",
        parse_mode="Markdown",
        reply_markup=Keyboards.cancel(),
    )
    await callback.answer()


@router.message(AdminStates.waiting_for_broadcast_message)
async def admin_broadcast_send(message: Message, state: FSMContext, session, user: User, bot: Bot):
    if not is_admin(user):
        return

    text = message.text or message.caption or ""
    status_msg = await message.answer("📢 Начинаю рассылку...")

    result = await session.execute(
        select(User.telegram_id).where(User.is_blocked == False)
    )
    telegram_ids = result.scalars().all()

    sent = 0
    failed = 0
    for tg_id in telegram_ids:
        try:
            await bot.send_message(tg_id, text, parse_mode="Markdown")
            sent += 1
        except Exception:
            failed += 1

    await status_msg.edit_text(
        f"✅ Рассылка завершена!\n\nОтправлено: {sent}\nОшибок: {failed}"
    )
    await state.clear()


@router.callback_query(F.data == "admin:users")
async def admin_users(callback: CallbackQuery, state: FSMContext, user: User):
    if not is_admin(user):
        await callback.answer("⛔ Нет доступа")
        return
    await state.set_state(AdminStates.waiting_for_user_search)
    await callback.message.edit_text(
        "👥 *Поиск пользователя*\n\nОтправь Telegram ID или @username:",
        parse_mode="Markdown",
        reply_markup=Keyboards.cancel(),
    )
    await callback.answer()


@router.message(AdminStates.waiting_for_user_search)
async def admin_user_search(message: Message, state: FSMContext, session, user: User):
    if not is_admin(user):
        return

    query = message.text.strip().lstrip("@")
    target = None

    try:
        tg_id = int(query)
        target = await get_user_by_telegram_id(session, tg_id)
    except ValueError:
        result = await session.execute(select(User).where(User.username == query))
        target = result.scalar_one_or_none()

    if not target:
        await message.answer("❌ Пользователь не найден")
        return

    text = (
        f"👤 *Пользователь*\n\n"
        f"ID: `{target.telegram_id}`\n"
        f"Username: @{target.username or '—'}\n"
        f"Имя: {target.first_name or '—'} {target.last_name or ''}\n"
        f"Баланс: {target.balance} треков\n"
        f"Всего создано: {target.total_generated}\n"
        f"Заблокирован: {'Да' if target.is_blocked else 'Нет'}\n"
        f"Зарегистрирован: {target.created_at.strftime('%d.%m.%Y')}"
    )
    await message.answer(text, parse_mode="Markdown")
    await state.clear()
