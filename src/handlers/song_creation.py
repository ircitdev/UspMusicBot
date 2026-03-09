import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.keyboards import Keyboards
from bot.states import SongCreationStates
from bot.texts import (
    SONG_MODE_SELECT, WAITING_FOR_IDEA, WAITING_FOR_LYRICS,
    GENERATING_LYRICS, LYRICS_GENERATED, GENERATING_SONG,
    SONG_READY, SONG_FAILED, NO_BALANCE, PROCESSING,
)
from database.crud import (
    deduct_credit, create_song, update_song_result, cache_lyrics,
    get_lyrics_cache, mark_lyrics_used
)
from database.models import User
from services import SunoClient, ClaudeClient
from config import settings
from utils.helpers import format_duration

router = Router()


def get_suno() -> SunoClient:
    return SunoClient(settings.suno_api_key, settings.suno_base_url)


def get_claude() -> ClaudeClient:
    return ClaudeClient(settings.anthropic_api_key)


@router.message(F.text == "🎵 Создать песню")
async def start_song_creation(message: Message, state: FSMContext, user: User):
    if user.balance <= 0:
        await message.answer(NO_BALANCE, parse_mode="Markdown", reply_markup=Keyboards.balance_menu())
        return
    await state.set_state(SongCreationStates.waiting_for_idea)
    await message.answer(WAITING_FOR_IDEA, parse_mode="Markdown", reply_markup=Keyboards.cancel())


@router.message(F.text == "📝 Есть стихи")
async def start_with_lyrics(message: Message, state: FSMContext, user: User):
    if user.balance <= 0:
        await message.answer(NO_BALANCE, parse_mode="Markdown", reply_markup=Keyboards.balance_menu())
        return
    await state.set_state(SongCreationStates.waiting_for_lyrics)
    await message.answer(WAITING_FOR_LYRICS, parse_mode="Markdown", reply_markup=Keyboards.cancel())


# ─── Режим 1: Идея → Текст → Музыка ──────────────────────────────────────────

@router.message(SongCreationStates.waiting_for_idea, F.text)
async def process_idea(message: Message, state: FSMContext, session, user: User):
    idea = message.text.strip()
    if len(idea) < 5:
        await message.answer("❌ Идея слишком короткая. Опиши подробнее!")
        return
    if len(idea) > 500:
        await message.answer("❌ Слишком длинное описание. Максимум 500 символов.")
        return

    status_msg = await message.answer(GENERATING_LYRICS, parse_mode="Markdown")
    await state.set_state(SongCreationStates.generating_lyrics)

    try:
        claude = get_claude()
        lyrics = await claude.generate_lyrics(idea)
        styles = await claude.suggest_styles(idea)

        cache = await cache_lyrics(session, user.id, idea, lyrics, [s["name"] for s in styles])

        await state.update_data(
            cache_id=cache.id,
            idea=idea,
            lyrics=lyrics,
        )

        await status_msg.delete()
        preview = lyrics[:800] + ("..." if len(lyrics) > 800 else "")
        await message.answer(
            LYRICS_GENERATED.format(lyrics=preview),
            parse_mode="Markdown",
            reply_markup=Keyboards.style_selection(styles, cache.id),
        )
        await state.set_state(SongCreationStates.waiting_for_style_choice)

    except Exception as e:
        logger.error(f"Lyrics generation error: {e}")
        await status_msg.delete()
        await message.answer("❌ Не удалось сгенерировать текст. Попробуй ещё раз.")
        await state.set_state(SongCreationStates.waiting_for_idea)


@router.callback_query(SongCreationStates.waiting_for_style_choice, F.data.startswith("style:"))
async def process_style_choice(callback: CallbackQuery, state: FSMContext, session, user: User, bot: Bot):
    parts = callback.data.split(":")
    style_desc = parts[1]
    cache_id = int(parts[2])

    if style_desc == "custom":
        await callback.message.edit_text(
            "✏️ Опиши свой музыкальный стиль:\n\nНапример: *мелодичный поп с пианино*",
            parse_mode="Markdown",
        )
        await state.update_data(cache_id=cache_id)
        await state.set_state(SongCreationStates.waiting_for_custom_style)
        await callback.answer()
        return

    await callback.answer(PROCESSING)
    await _generate_song_from_cache(callback.message, state, session, user, bot, cache_id, style_desc)


@router.message(SongCreationStates.waiting_for_custom_style, F.text)
async def process_custom_style(message: Message, state: FSMContext, session, user: User, bot: Bot):
    style = message.text.strip()[:100]
    data = await state.get_data()
    cache_id = data.get("cache_id")
    await _generate_song_from_cache(message, state, session, user, bot, cache_id, style)


# ─── Режим 2: Готовый текст → Музыка ─────────────────────────────────────────

@router.message(SongCreationStates.waiting_for_lyrics, F.text)
async def process_user_lyrics(message: Message, state: FSMContext, session, user: User):
    lyrics = message.text.strip()
    if len(lyrics) < 20:
        await message.answer("❌ Текст слишком короткий. Минимум 20 символов.")
        return
    if len(lyrics) > settings.max_lyrics_length:
        await message.answer(f"❌ Текст слишком длинный. Максимум {settings.max_lyrics_length} символов.")
        return

    await state.update_data(lyrics=lyrics, idea="Готовый текст")
    await message.answer(
        "✨ *Отличный текст!* Теперь выбери стиль музыки:",
        parse_mode="Markdown",
        reply_markup=Keyboards.lyrics_style_selection(),
    )
    await state.set_state(SongCreationStates.waiting_for_lyrics_style)


@router.callback_query(SongCreationStates.waiting_for_lyrics_style, F.data.startswith("lstyle:"))
async def process_lyrics_style(callback: CallbackQuery, state: FSMContext, session, user: User, bot: Bot):
    style = callback.data.split(":", 1)[1]
    data = await state.get_data()
    lyrics = data.get("lyrics", "")

    if style == "custom":
        await callback.message.edit_text(
            "✏️ Опиши свой стиль:\n\nНапример: *джаз с саксофоном*",
            parse_mode="Markdown",
        )
        await state.set_state(SongCreationStates.waiting_for_custom_style)
        await callback.answer()
        return

    await callback.answer(PROCESSING)

    cache = await cache_lyrics(session, user.id, "Готовый текст", lyrics, [style])
    await _generate_song_from_cache(callback.message, state, session, user, bot, cache.id, style)


# ─── Генерация трека ──────────────────────────────────────────────────────────

async def _generate_song_from_cache(
    message, state: FSMContext, session, user: User, bot: Bot, cache_id: int, style: str
):
    data = await state.get_data()
    lyrics = data.get("lyrics", "")
    idea = data.get("idea", "")

    if not lyrics:
        cache = await get_lyrics_cache(session, cache_id)
        if cache:
            lyrics = cache.generated_lyrics
            idea = cache.prompt

    if not await deduct_credit(session, user.id):
        await message.answer(NO_BALANCE, parse_mode="Markdown", reply_markup=Keyboards.balance_menu())
        await state.clear()
        return

    status_msg = await message.answer(GENERATING_SONG, parse_mode="Markdown")
    await state.set_state(SongCreationStates.generating_song)

    try:
        suno = get_suno()
        claude = get_claude()

        title = await claude.refine_title(lyrics, idea)
        result = await suno.generate_song(lyrics=lyrics, style=style, prompt=idea)
        task_id = result.get("task_id") or result.get("id")

        song = await create_song(
            session=session,
            user_id=user.id,
            prompt=idea,
            lyrics=lyrics,
            style=style,
            suno_task_id=task_id,
            title=title,
        )

        if cache_id:
            await mark_lyrics_used(session, cache_id)

        completed = await suno.wait_for_completion(
            task_id=task_id,
            max_wait=settings.suno_max_wait,
            poll_interval=settings.suno_poll_interval,
        )

        await status_msg.delete()

        if not completed:
            await _handle_song_failure(message, session, user.id, song.id, state)
            return

        audio_url = completed.get("audio_url", "")
        duration_sec = completed.get("duration", 0)

        await update_song_result(session, song.id, audio_url, duration_sec)

        duration_str = format_duration(duration_sec)
        sent = await bot.send_audio(
            chat_id=message.chat.id,
            audio=audio_url,
            title=title,
            performer="UspMusicBot",
            caption=SONG_READY.format(title=title, duration=duration_str, style=style),
            parse_mode="Markdown",
            reply_markup=Keyboards.song_result(song.id),
        )

        if sent.audio:
            from database.crud import set_song_file_id
            await set_song_file_id(session, song.id, sent.audio.file_id)

        await state.clear()

    except Exception as e:
        logger.error(f"Song generation error for user {user.id}: {e}")
        try:
            await status_msg.delete()
        except Exception:
            pass
        await _handle_song_failure(message, session, user.id, None, state)


async def _handle_song_failure(message, session, user_id: int, song_id, state: FSMContext):
    await update_user_balance(session, user_id, 1)  # Возврат кредита
    await message.answer(SONG_FAILED, parse_mode="Markdown", reply_markup=Keyboards.main_menu())
    await state.clear()
