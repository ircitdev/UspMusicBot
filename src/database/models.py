from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, BigInteger,
    ForeignKey, Text, Numeric, Date, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .engine import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    balance = Column(Integer, default=3)
    total_generated = Column(Integer, default=0)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    language_code = Column(String(10), default="ru")
    is_admin = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    last_active_at = Column(DateTime, default=func.now(), onupdate=func.now())

    songs = relationship("Song", back_populates="user", lazy="dynamic")
    transactions = relationship("Transaction", back_populates="user", lazy="dynamic")
    playlists = relationship("Playlist", back_populates="user", lazy="dynamic")
    referrals = relationship("User", backref="referrer", remote_side=[id])

    def __repr__(self):
        return f"<User id={self.id} tg={self.telegram_id} balance={self.balance}>"


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255))
    lyrics = Column(Text)
    prompt = Column(String(500))
    style = Column(String(100))
    suno_task_id = Column(String(255))
    telegram_file_id = Column(String(255))
    audio_url = Column(Text)
    duration = Column(Integer)
    generation_cost = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now(), index=True)

    user = relationship("User", back_populates="songs")
    playlist_songs = relationship("PlaylistSong", back_populates="song")

    def __repr__(self):
        return f"<Song id={self.id} title={self.title} user_id={self.user_id}>"


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="playlists")
    playlist_songs = relationship("PlaylistSong", back_populates="playlist", cascade="all, delete-orphan")


class PlaylistSong(Base):
    __tablename__ = "playlist_songs"
    __table_args__ = (UniqueConstraint("playlist_id", "song_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    added_at = Column(DateTime, default=func.now())

    playlist = relationship("Playlist", back_populates="playlist_songs")
    song = relationship("Song", back_populates="playlist_songs")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    payment_id = Column(String(255), unique=True)
    provider = Column(String(50))
    credits_amount = Column(Integer, nullable=False)
    price_amount = Column(Numeric(10, 2))
    price_currency = Column(String(10))
    status = Column(String(50), default="pending", index=True)
    extra_data = Column("metadata", Text)
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)

    user = relationship("User", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction id={self.id} status={self.status} credits={self.credits_amount}>"


class LyricsCache(Base):
    __tablename__ = "lyrics_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    prompt = Column(String(500))
    generated_lyrics = Column(Text)
    style_suggestions = Column(Text)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


class AnalyticsDaily(Base):
    __tablename__ = "analytics_daily"

    date = Column(Date, primary_key=True)
    new_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    songs_generated = Column(Integer, default=0)
    revenue_rub = Column(Numeric(10, 2), default=0)
    revenue_crypto = Column(Numeric(10, 2), default=0)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
