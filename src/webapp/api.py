from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from .auth import validate_telegram_data

app = FastAPI(title="UspMusicBot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SongRequest(BaseModel):
    init_data: str
    lyrics: Optional[str] = None
    style: Optional[str] = None


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/songs/create")
async def create_song_webapp(request: SongRequest):
    user_data = validate_telegram_data(request.init_data)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid Telegram data")
    # TODO: Интеграция с основным ботом
    return {"status": "accepted", "message": "Song creation queued"}


@app.get("/api/songs/{user_id}")
async def get_user_songs_api(user_id: int, init_data: str):
    user_data = validate_telegram_data(init_data)
    if not user_data or user_data.get("id") != user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # TODO: Получение песен из БД
    return {"songs": [], "total": 0}
