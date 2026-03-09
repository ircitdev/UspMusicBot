import asyncio
from typing import Optional, Dict, List
import httpx
from loguru import logger


class SunoClient:
    def __init__(self, api_key: str, base_url: str = "https://api.aimlapi.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def generate_song(
        self,
        lyrics: str,
        style: str,
        prompt: Optional[str] = None,
        make_instrumental: bool = False,
    ) -> Dict:
        payload = {
            "gpt_description": prompt or f"{style} song",
            "lyrics": lyrics,
            "style": style,
            "make_instrumental": make_instrumental,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/generate",
                json=payload,
                headers=self.headers,
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"Suno generate response: {data}")
            return data

    async def get_task_status(self, task_id: str) -> Dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def wait_for_completion(
        self,
        task_id: str,
        max_wait: int = 120,
        poll_interval: int = 5,
    ) -> Optional[Dict]:
        elapsed = 0
        while elapsed < max_wait:
            try:
                result = await self.get_task_status(task_id)
                status = result.get("status", "")

                if status == "completed":
                    logger.info(f"Task {task_id} completed: {result}")
                    return result
                elif status == "failed":
                    error = result.get("error", "Unknown error")
                    raise RuntimeError(f"Suno generation failed: {error}")

                logger.debug(f"Task {task_id} status: {status}, elapsed: {elapsed}s")
            except httpx.HTTPError as e:
                logger.warning(f"HTTP error polling task {task_id}: {e}")

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        logger.warning(f"Task {task_id} timed out after {max_wait}s")
        return None

    def get_style_suggestions(self, theme: str) -> List[Dict]:
        theme_lower = theme.lower()
        styles = [
            {"name": "Pop", "emoji": "🎵", "description": "pop"},
            {"name": "Pop Rock", "emoji": "🎸", "description": "pop rock"},
            {"name": "Electronic", "emoji": "🎹", "description": "electronic dance"},
            {"name": "R&B", "emoji": "🎤", "description": "r&b soul"},
            {"name": "Hip-hop", "emoji": "🎧", "description": "hip hop"},
            {"name": "Jazz", "emoji": "🎺", "description": "jazz"},
            {"name": "Classical", "emoji": "🎻", "description": "classical orchestral"},
            {"name": "Folk", "emoji": "🪕", "description": "folk acoustic"},
        ]

        if any(w in theme_lower for w in ["грустн", "печал", "тоск", "слез"]):
            priority = ["R&B", "Jazz", "Folk"]
        elif any(w in theme_lower for w in ["весел", "радост", "танц", "вечер"]):
            priority = ["Pop", "Electronic", "Hip-hop"]
        elif any(w in theme_lower for w in ["рок", "силь", "мощ", "бунт"]):
            priority = ["Pop Rock", "Electronic", "Hip-hop"]
        else:
            priority = ["Pop", "Pop Rock", "Electronic"]

        ordered = sorted(styles, key=lambda s: (0 if s["name"] in priority else 1, styles.index(s)))
        return ordered[:3]
