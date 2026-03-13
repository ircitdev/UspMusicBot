# UspMusicBot

Telegram-бот для генерации музыки через AI (@UspMusicCreatorBot).

## Tech Stack

- **Python 3.10+**, aiogram 3.15.0, SQLAlchemy 2.0 async, Pydantic Settings
- **APIs**: Suno (через AIMLAPI), Claude (Anthropic), OpenAI Whisper, YooKassa
- **DB**: SQLite + aiosqlite
- **FSM**: MemoryStorage (Redis опционально)

## Project Structure

```
src/
  bot/          # main.py (entry point), middleware.py, keyboards.py, states.py, texts.py
  handlers/     # start, song_creation, voice, balance, playlists, admin, callbacks
  services/     # suno_client, claude_client, whisper_client, payment_service
  database/     # models.py, crud.py, engine.py
  utils/        # logger, helpers
  webapp/       # FastAPI endpoints
  config.py     # Pydantic Settings, loads .env
```

## Running

```bash
# Local
cd UspMusicBot && PYTHONPATH=src python src/bot/main.py

# Server (pm2)
pm2 start ecosystem.config.js
```

## Deployment

- **Server**: 31.44.7.144 (root), path: `/root/bots/usp/UspMusicBot/`
- **Process manager**: pm2, name: `uspmusicbot`
- **Update**: `scp -r src root@31.44.7.144:/root/bots/usp/UspMusicBot/ && ssh root@31.44.7.144 "pm2 restart uspmusicbot"`

## Key Conventions

- Run from project root (not src/) — `.env` is loaded relative to cwd
- `PYTHONPATH=src` required for imports
- `Transaction.extra_data` maps to DB column `metadata` (SQLAlchemy reserved name workaround)
- `admin_ids` validator handles both string ("65876198") and int (65876198) from .env
- IPv4 connector fix in main.py for Windows aiohttp DNS issues (not needed on Linux)
- Middleware registered on `dp.message` and `dp.callback_query` (not `dp.update`)
- Bot uses `ParseMode.MARKDOWN` as default

## GitHub

- Repo: https://github.com/ircitdev/UspMusicBot
- `.env` excluded via `.gitignore`
