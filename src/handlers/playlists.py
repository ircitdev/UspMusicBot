from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from loguru import logger

from bot.keyboards import Keyboards
from database.crud import get_user_songs, get_user_songs_count, get_song_by_id
from database.models import User
from utils.helpers import format_duration

router = Router()


@router.message(F.text == "🎧 Мои песни")
async def my_songs(message: Message, session, user: User):
    await show_songs_page(message, session, user, page=1, edit=False)


@router.callback_query(F.data == "songs:list")
async def songs_list_callback(callback: CallbackQuery, session, user: User):
    await show_songs_page(callback.message, session, user, page=1, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("songs:page:"))
async def songs_page(callback: CallbackQuery, session, user: User):
    page = int(callback.data.split(":")[-1])
    await show_songs_page(callback.message, session, user, page=page, edit=True)
    await callback.answer()


async def show_songs_page(message, session, user: User, page: int = 1, edit: bool = False):
    per_page = 5
    total = await get_user_songs_count(session, user.id)

    if total == 0:
        text = "🎵 *Мои песни*\n\nУ тебя ещё нет созданных песен.\n\nНажми *🎵 Создать песню*!"
        kb = Keyboards.main_menu()
        if edit:
            await message.edit_text(text, parse_mode="Markdown")
        else:
            await message.answer(text, parse_mode="Markdown", reply_markup=kb)
        return

    songs = await get_user_songs(session, user.id, page=page, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page

    lines = [f"🎵 *Мои песни* ({total})\nСтраница {page}/{total_pages}:\n"]
    for i, song in enumerate(songs, start=(page - 1) * per_page + 1):
        dur = format_duration(song.duration) if song.duration else "?"
        date_str = song.created_at.strftime("%d.%m.%Y")
        lines.append(f"{i}. *{song.title or 'Без названия'}* — {dur}")
        lines.append(f"   📅 {date_str} | 🎨 {song.style or '?'}")

    text = "\n".join(lines)
    kb = Keyboards.my_songs(page=page, total=total, per_page=per_page)

    if edit:
        await message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await message.answer(text, parse_mode="Markdown", reply_markup=kb)


@router.callback_query(F.data.startswith("song:download:"))
async def song_download(callback: CallbackQuery, session, user: User):
    song_id = int(callback.data.split(":")[-1])
    song = await get_song_by_id(session, song_id)

    if not song or song.user_id != user.id:
        await callback.answer("❌ Песня не найдена")
        return

    if song.telegram_file_id:
        await callback.message.answer_audio(
            audio=song.telegram_file_id,
            title=song.title or "Песня",
            performer="UspMusicBot",
            caption=f"🎵 *{song.title}*\n🎨 {song.style}",
            parse_mode="Markdown",
        )
    elif song.audio_url:
        await callback.message.answer_audio(
            audio=song.audio_url,
            title=song.title or "Песня",
            performer="UspMusicBot",
        )
    else:
        await callback.answer("❌ Аудио недоступно")
        return

    await callback.answer()


@router.callback_query(F.data == "song:new")
async def new_song(callback: CallbackQuery):
    await callback.message.answer(
        "🎵 Начинаем создание новой песни!",
        reply_markup=Keyboards.main_menu(),
    )
    await callback.answer()
