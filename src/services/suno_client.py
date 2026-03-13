import asyncio
from typing import Optional, Dict, List
import httpx
from loguru import logger


class SunoClient:
    """Suno AI music generation via AIMLAPI v2 endpoint."""

    GENERATE_URL = "https://api.aimlapi.com/v2/generate/audio/suno-ai/clip"

    def __init__(self, api_key: str, base_url: str = "https://api.aimlapi.com"):
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
        """Generate a song clip. Returns dict with clip_ids."""
        payload = {
            "prompt": lyrics,
            "tags": style,
            "title": prompt or f"{style} song",
            "make_instrumental": make_instrumental,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                self.GENERATE_URL,
                json=payload,
                headers=self.headers,
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"Suno generate response: {data}")
            # Response contains clip_ids list
            return data

    async def get_clip_status(self, clip_id: str) -> Dict:
        """Fetch clip status and data."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                self.GENERATE_URL,
                params={"clip_id": clip_id},
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    # Keep backward compatibility
    async def get_task_status(self, task_id: str) -> Dict:
        return await self.get_clip_status(task_id)

    async def wait_for_completion(
        self,
        clip_id: str,
        max_wait: int = 180,
        poll_interval: int = 5,
    ) -> Optional[Dict]:
        """Poll until clip is complete. Returns clip data or None on timeout."""
        elapsed = 0
        while elapsed < max_wait:
            try:
                result = await self.get_clip_status(clip_id)
                status = result.get("status", "")

                if status == "complete":
                    logger.info(f"Clip {clip_id} complete")
                    return result
                elif status == "error":
                    error = result.get("error", "Unknown error")
                    raise RuntimeError(f"Suno generation failed: {error}")

                logger.debug(f"Clip {clip_id} status: {status}, elapsed: {elapsed}s")
            except httpx.HTTPError as e:
                logger.warning(f"HTTP error polling clip {clip_id}: {e}")

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        logger.warning(f"Clip {clip_id} timed out after {max_wait}s")
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
