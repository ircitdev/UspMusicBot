from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards import Keyboards

router = Router()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Действие отменено.",
        reply_markup=None,
    )
    await callback.message.answer(
        "Выбери действие:",
        reply_markup=Keyboards.main_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "playlist:add:")
async def playlist_add(callback: CallbackQuery):
    await callback.answer("📋 Плейлисты будут доступны в версии 2.0!", show_alert=True)
