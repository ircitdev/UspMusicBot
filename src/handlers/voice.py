from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.keyboards import Keyboards
from bot.states import SongCreationStates
from bot.texts import VOICE_TRANSCRIBED
from database.models import User
from services import WhisperClient
from config import settings

router = Router()


def get_whisper() -> WhisperClient:
    return WhisperClient(settings.openai_api_key)


@router.message(F.voice | F.audio)
async def handle_voice(message: Message, state: FSMContext, bot: Bot, user: User):
    current_state = await state.get_state()

    # Голосовые принимаем только в ожидании идеи или в любом начальном состоянии
    if current_state not in (None, SongCreationStates.waiting_for_idea):
        await message.answer("❌ В данный момент я не принимаю голосовые. Используй текст.")
        return

    if user.balance <= 0:
        await message.answer(
            "❌ Недостаточно кредитов для создания песни.",
            reply_markup=Keyboards.balance_menu()
        )
        return

    status_msg = await message.answer("🎤 Слушаю... Транскрибирую аудио.")

    try:
        file_obj = message.voice or message.audio

        if file_obj.duration and file_obj.duration > settings.max_voice_duration:
            await status_msg.delete()
            await message.answer(
                f"❌ Слишком длинное аудио. Максимум {settings.max_voice_duration // 60} минут."
            )
            return

        file = await bot.get_file(file_obj.file_id)
        file_bytes = await bot.download_file(file.file_path)

        whisper = get_whisper()
        ext = ".ogg" if message.voice else ".mp3"
        text = await whisper.transcribe(file_bytes.read(), filename=f"voice{ext}")

        await status_msg.delete()

        if not text:
            await message.answer("❌ Не удалось распознать речь. Попробуй снова.")
            return

        await state.update_data(voice_text=text)
        await state.set_state(SongCreationStates.waiting_for_idea)

        await message.answer(
            VOICE_TRANSCRIBED.format(text=text),
            parse_mode="Markdown",
            reply_markup=Keyboards.voice_confirm(text),
        )

    except Exception as e:
        logger.error(f"Voice handling error: {e}")
        try:
            await status_msg.delete()
        except Exception:
            pass
        await message.answer("❌ Ошибка при обработке голоса. Попробуй отправить текстом.")


@router.callback_query(F.data == "voice:confirm")
async def voice_confirm(callback, state: FSMContext, session, user: User, bot: Bot):
    data = await state.get_data()
    text = data.get("voice_text", "")
    if not text:
        await callback.answer("Ошибка: текст не найден")
        return

    await callback.message.edit_text(f"💡 Создаю песню на тему: *{text[:100]}*", parse_mode="Markdown")
    await state.update_data(idea=text, lyrics="")
    await state.set_state(SongCreationStates.generating_lyrics)

    from handlers.song_creation import process_idea
    fake_msg = callback.message
    fake_msg.text = text
    await process_idea(fake_msg, state, session, user)
    await callback.answer()


@router.callback_query(F.data == "voice:edit")
async def voice_edit(callback, state: FSMContext):
    await state.set_state(SongCreationStates.waiting_for_idea)
    await callback.message.edit_text(
        "✏️ Отправь исправленный текст идеи:",
        reply_markup=Keyboards.cancel()
    )
    await callback.answer()
