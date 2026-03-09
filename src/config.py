from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    # Telegram
    bot_token: str
    admin_ids: List[int] = []

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/uspmusic.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # AI Services
    anthropic_api_key: str
    openai_api_key: str
    suno_api_key: str
    suno_base_url: str = "https://api.aimlapi.com/v1"

    # Payments
    yookassa_shop_id: str = ""
    yookassa_secret_key: str = ""
    cryptobot_api_token: str = ""

    # Web App
    webapp_url: str = ""
    webhook_url: str = ""
    webhook_secret: str = ""

    # App Settings
    debug: bool = False
    log_level: str = "INFO"
    max_voice_duration: int = 300
    max_lyrics_length: int = 3000
    free_credits_on_start: int = 3
    suno_poll_interval: int = 5
    suno_max_wait: int = 120

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(i.strip()) for i in v.split(",") if i.strip()]
        if isinstance(v, int):
            return [v]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
