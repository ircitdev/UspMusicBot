from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards import Keyboards
from bot.texts import BALANCE_INFO, BALANCE_EMPTY_HISTORY
from database.crud import get_user_transactions
from database.models import User
from services.payment_service import PaymentService
from config import settings

router = Router()


def get_payment_service() -> PaymentService:
    return PaymentService(
        yookassa_shop_id=settings.yookassa_shop_id,
        yookassa_secret_key=settings.yookassa_secret_key,
        cryptobot_token=settings.cryptobot_api_token,
        return_url=f"https://t.me/UspMusicBot",
    )


@router.message(F.text == "💳 Баланс")
async def show_balance(message: Message, session, user: User):
    transactions = await get_user_transactions(session, user.id, limit=5)

    if transactions:
        history_lines = []
        for t in transactions:
            date_str = t.created_at.strftime("%d.%m.%Y")
            if t.status == "completed":
                history_lines.append(f"• {date_str}: +{t.credits_amount} треков ({t.price_amount}₽)")
            else:
                history_lines.append(f"• {date_str}: {t.status} ({t.credits_amount} треков)")
        history_text = "\n".join(history_lines)
    else:
        history_text = BALANCE_EMPTY_HISTORY

    text = BALANCE_INFO.format(
        balance=user.balance,
        total_generated=user.total_generated,
        history=history_text,
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=Keyboards.balance_menu())


@router.callback_query(F.data == "balance:main")
async def balance_main(callback: CallbackQuery, session, user: User):
    await callback.message.edit_text(
        f"💳 *Баланс*\n\nДоступно треков: *{user.balance}* 🎵\n\nВыбери пакет для пополнения:",
        parse_mode="Markdown",
        reply_markup=Keyboards.balance_menu(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy:"))
async def buy_package(callback: CallbackQuery, user: User):
    package_id = callback.data.split(":", 1)[1]
    await callback.message.edit_reply_markup(
        reply_markup=Keyboards.payment_method(package_id)
    )

    payment_service = get_payment_service()
    package = payment_service.get_package(package_id)
    if package:
        await callback.message.edit_text(
            f"📦 *{package['name']}*\n\n"
            f"🎵 {package['credits']} треков\n"
            f"💰 {package['price']:.0f}₽\n\n"
            f"Выбери способ оплаты:",
            parse_mode="Markdown",
            reply_markup=Keyboards.payment_method(package_id),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("pay:yookassa:"))
async def pay_yookassa(callback: CallbackQuery, user: User):
    package_id = callback.data.split(":", 2)[2]
    payment_service = get_payment_service()

    await callback.answer("Создаю платёж...")
    result = await payment_service.create_yookassa_payment(user.id, package_id)

    if result:
        await callback.message.edit_text(
            f"💳 *Оплата картой*\n\n"
            f"Сумма: {result['amount']:.0f}₽\n"
            f"Треков: {result['credits']}\n\n"
            f"Нажми кнопку ниже для оплаты:",
            parse_mode="Markdown",
            reply_markup=Keyboards.payment_link(result["confirmation_url"], package_id),
        )
    else:
        await callback.message.answer(
            "❌ YooKassa не настроена. Обратитесь к администратору."
        )


@router.callback_query(F.data.startswith("pay:check:"))
async def check_payment(callback: CallbackQuery, session, user: User):
    await callback.message.edit_text(
        "⏳ Проверяю оплату...\n\nЕсли деньги списаны, кредиты будут начислены автоматически.\n"
        "Если нет — попробуй ещё раз или напиши в поддержку.",
        parse_mode="Markdown",
    )
    await callback.answer("Проверяю...")


@router.callback_query(F.data == "balance:history")
async def balance_history(callback: CallbackQuery, session, user: User):
    transactions = await get_user_transactions(session, user.id, limit=10)

    if not transactions:
        await callback.answer("История пуста")
        return

    lines = [f"📊 *История транзакций*\n"]
    for t in transactions:
        date_str = t.created_at.strftime("%d.%m.%Y %H:%M")
        status_icon = "✅" if t.status == "completed" else ("⏳" if t.status == "pending" else "❌")
        lines.append(f"{status_icon} {date_str}: +{t.credits_amount} треков")
        if t.price_amount:
            lines.append(f"   {t.price_amount}₽ ({t.provider})")

    await callback.message.edit_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=Keyboards.cancel(),
    )
    await callback.answer()
