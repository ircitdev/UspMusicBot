from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards import Keyboards
from bot.texts import WELCOME, WELCOME_BACK, HELP_TEXT
from database.crud import get_or_create_user, update_user_balance
from database.models import User
from config import settings

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session, user: User, is_new_user: bool):
    await state.clear()

    # Обработка реферального кода
    payload = message.text.split(" ", 1)[1] if " " in message.text else ""
    if payload.startswith("ref") and is_new_user:
        try:
            referrer_telegram_id = int(payload[3:])
            from database.crud import get_user_by_telegram_id
            referrer = await get_user_by_telegram_id(session, referrer_telegram_id)
            if referrer and referrer.id != user.id:
                await update_user_balance(session, referrer.id, 2)
                await update_user_balance(session, user.id, 2)
        except (ValueError, Exception):
            pass

    if is_new_user:
        await message.answer(
            WELCOME.format(balance=user.balance),
            parse_mode="Markdown",
            reply_markup=Keyboards.main_menu(),
        )
    else:
        name = user.first_name or user.username or "Музыкант"
        await message.answer(
            WELCOME_BACK.format(name=name, balance=user.balance),
            parse_mode="Markdown",
            reply_markup=Keyboards.main_menu(),
        )


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, parse_mode="Markdown")


@router.message(Command("admin"))
async def cmd_admin(message: Message, user: User):
    if user.telegram_id not in settings.admin_ids and not user.is_admin:
        return
    from bot.keyboards import Keyboards
    await message.answer("🔐 *Админ-панель*", parse_mode="Markdown", reply_markup=Keyboards.admin_menu())


@router.message(Command("referral"))
async def cmd_referral(message: Message, user: User):
    link = f"https://t.me/UspMusicBot?start=ref{user.telegram_id}"
    await message.answer(
        f"🔗 *Реферальная ссылка*\n\n"
        f"Поделись с друзьями:\n`{link}`\n\n"
        f"За каждого приглашённого:\n"
        f"• Ты получишь: +2 трека\n"
        f"• Друг получит: +2 трека",
        parse_mode="Markdown",
    )
