from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import date, datetime
import json

from .models import User, Song, Transaction, Playlist, PlaylistSong, LyricsCache, AnalyticsDaily


# ─── Users ────────────────────────────────────────────────────────────────────

async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    language_code: str = "ru",
    referrer_id: Optional[int] = None,
    free_credits: int = 3,
) -> tuple[User, bool]:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    created = False

    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            referrer_id=referrer_id,
            balance=free_credits,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        created = True
    else:
        await session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(
                username=username,
                first_name=first_name,
                last_name=last_name,
                last_active_at=func.now(),
            )
        )
        await session.commit()
        await session.refresh(user)

    return user, created


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def update_user_balance(session: AsyncSession, user_id: int, delta: int) -> int:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError(f"User {user_id} not found")
    user.balance = max(0, user.balance + delta)
    await session.commit()
    return user.balance


async def deduct_credit(session: AsyncSession, user_id: int) -> bool:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or user.balance <= 0:
        return False
    user.balance -= 1
    user.total_generated += 1
    await session.commit()
    return True


async def set_user_admin(session: AsyncSession, user_id: int, is_admin: bool):
    await session.execute(update(User).where(User.id == user_id).values(is_admin=is_admin))
    await session.commit()


async def block_user(session: AsyncSession, user_id: int, blocked: bool):
    await session.execute(update(User).where(User.id == user_id).values(is_blocked=blocked))
    await session.commit()


async def get_total_users_count(session: AsyncSession) -> int:
    result = await session.execute(select(func.count()).select_from(User))
    return result.scalar()


# ─── Songs ────────────────────────────────────────────────────────────────────

async def create_song(
    session: AsyncSession,
    user_id: int,
    prompt: str,
    lyrics: str,
    style: str,
    suno_task_id: str,
    title: Optional[str] = None,
) -> Song:
    song = Song(
        user_id=user_id,
        prompt=prompt,
        lyrics=lyrics,
        style=style,
        suno_task_id=suno_task_id,
        title=title or f"Песня #{suno_task_id[:6]}",
    )
    session.add(song)
    await session.commit()
    await session.refresh(song)
    return song


async def update_song_result(
    session: AsyncSession,
    song_id: int,
    audio_url: str,
    duration: int,
    telegram_file_id: Optional[str] = None,
):
    await session.execute(
        update(Song)
        .where(Song.id == song_id)
        .values(audio_url=audio_url, duration=duration, telegram_file_id=telegram_file_id)
    )
    await session.commit()


async def set_song_file_id(session: AsyncSession, song_id: int, file_id: str):
    await session.execute(update(Song).where(Song.id == song_id).values(telegram_file_id=file_id))
    await session.commit()


async def get_user_songs(session: AsyncSession, user_id: int, page: int = 1, per_page: int = 5) -> List[Song]:
    offset = (page - 1) * per_page
    result = await session.execute(
        select(Song)
        .where(Song.user_id == user_id)
        .order_by(desc(Song.created_at))
        .offset(offset)
        .limit(per_page)
    )
    return result.scalars().all()


async def get_user_songs_count(session: AsyncSession, user_id: int) -> int:
    result = await session.execute(select(func.count()).select_from(Song).where(Song.user_id == user_id))
    return result.scalar()


async def get_song_by_id(session: AsyncSession, song_id: int) -> Optional[Song]:
    result = await session.execute(select(Song).where(Song.id == song_id))
    return result.scalar_one_or_none()


# ─── Lyrics Cache ─────────────────────────────────────────────────────────────

async def cache_lyrics(
    session: AsyncSession,
    user_id: int,
    prompt: str,
    lyrics: str,
    style_suggestions: List[str],
) -> LyricsCache:
    entry = LyricsCache(
        user_id=user_id,
        prompt=prompt,
        generated_lyrics=lyrics,
        style_suggestions=json.dumps(style_suggestions, ensure_ascii=False),
    )
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


async def get_lyrics_cache(session: AsyncSession, cache_id: int) -> Optional[LyricsCache]:
    result = await session.execute(select(LyricsCache).where(LyricsCache.id == cache_id))
    return result.scalar_one_or_none()


async def mark_lyrics_used(session: AsyncSession, cache_id: int):
    await session.execute(update(LyricsCache).where(LyricsCache.id == cache_id).values(used=True))
    await session.commit()


# ─── Transactions ─────────────────────────────────────────────────────────────

async def create_transaction(
    session: AsyncSession,
    user_id: int,
    payment_id: str,
    provider: str,
    credits_amount: int,
    price_amount: float,
    price_currency: str,
    extra_data: Optional[dict] = None,
) -> Transaction:
    txn = Transaction(
        user_id=user_id,
        payment_id=payment_id,
        provider=provider,
        credits_amount=credits_amount,
        price_amount=price_amount,
        price_currency=price_currency,
        extra_data=json.dumps(extra_data or {}, ensure_ascii=False),
    )
    session.add(txn)
    await session.commit()
    await session.refresh(txn)
    return txn


async def complete_transaction(session: AsyncSession, payment_id: str) -> Optional[Transaction]:
    result = await session.execute(select(Transaction).where(Transaction.payment_id == payment_id))
    txn = result.scalar_one_or_none()
    if txn and txn.status == "pending":
        txn.status = "completed"
        txn.completed_at = datetime.utcnow()
        await session.commit()
        await update_user_balance(session, txn.user_id, txn.credits_amount)
    return txn


async def get_user_transactions(session: AsyncSession, user_id: int, limit: int = 10) -> List[Transaction]:
    result = await session.execute(
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(desc(Transaction.created_at))
        .limit(limit)
    )
    return result.scalars().all()


# ─── Analytics ────────────────────────────────────────────────────────────────

async def update_daily_analytics(
    session: AsyncSession,
    new_users: int = 0,
    active_users: int = 0,
    songs_generated: int = 0,
    revenue_rub: float = 0,
    revenue_crypto: float = 0,
):
    today = date.today()
    result = await session.execute(select(AnalyticsDaily).where(AnalyticsDaily.date == today))
    row = result.scalar_one_or_none()

    if row:
        row.new_users += new_users
        row.active_users = max(row.active_users, active_users)
        row.songs_generated += songs_generated
        row.revenue_rub += revenue_rub
        row.revenue_crypto += revenue_crypto
    else:
        row = AnalyticsDaily(
            date=today,
            new_users=new_users,
            active_users=active_users,
            songs_generated=songs_generated,
            revenue_rub=revenue_rub,
            revenue_crypto=revenue_crypto,
        )
        session.add(row)

    await session.commit()
