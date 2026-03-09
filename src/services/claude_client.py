from anthropic import AsyncAnthropic
from typing import List, Optional
from loguru import logger


LYRICS_SYSTEM_PROMPT = """Ты профессиональный автор текстов песен.
Создавай структурированные, ритмичные тексты на русском языке.
Используй разметку: [Verse 1], [Verse 2], [Chorus], [Bridge], [Outro].
Тексты должны быть эмоциональными, образными и подходить для пения."""

LYRICS_TEMPLATE = """Создай текст песни на тему: "{theme}"

Требования:
- Язык: русский
- Структура: 2 куплета, припев (повторяется), бридж (опционально)
- Длина: 150-250 слов
- Стиль: соответствует теме
- Каждый раздел помечай: [Verse 1], [Chorus] и т.д.

Верни только текст песни, без объяснений."""

STYLE_PROMPT = """На основе темы песни "{theme}" предложи 3 музыкальных стиля.
Ответь в формате JSON (только JSON, без markdown):
[
  {{"name": "Pop", "emoji": "🎵", "description": "pop upbeat"}},
  {{"name": "Electronic", "emoji": "🎹", "description": "electronic dance"}},
  {{"name": "Folk", "emoji": "🪕", "description": "acoustic folk"}}
]"""


class ClaudeClient:
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = "claude-haiku-4-5-20251001"

    async def generate_lyrics(self, theme: str) -> str:
        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=LYRICS_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": LYRICS_TEMPLATE.format(theme=theme)}],
            )
            lyrics = message.content[0].text.strip()
            logger.info(f"Generated lyrics for theme: {theme[:50]}")
            return lyrics
        except Exception as e:
            logger.error(f"Claude lyrics generation failed: {e}")
            raise

    async def suggest_styles(self, theme: str) -> List[dict]:
        import json
        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=256,
                messages=[{"role": "user", "content": STYLE_PROMPT.format(theme=theme)}],
            )
            raw = message.content[0].text.strip()
            styles = json.loads(raw)
            return styles[:3]
        except Exception as e:
            logger.warning(f"Claude style suggestion failed: {e}, using defaults")
            return [
                {"name": "Pop", "emoji": "🎵", "description": "pop"},
                {"name": "Pop Rock", "emoji": "🎸", "description": "pop rock"},
                {"name": "Electronic", "emoji": "🎹", "description": "electronic"},
            ]

    async def refine_title(self, lyrics: str, theme: str) -> str:
        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=64,
                messages=[{
                    "role": "user",
                    "content": f"Придумай короткое название (2-4 слова) для песни на тему '{theme}'. Ответь только названием, без кавычек."
                }],
            )
            title = message.content[0].text.strip().strip('"').strip("'")
            return title[:100]
        except Exception as e:
            logger.warning(f"Title refinement failed: {e}")
            return f"Песня о {theme[:30]}"
