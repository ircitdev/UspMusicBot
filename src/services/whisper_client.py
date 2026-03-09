import os
import tempfile
from openai import AsyncOpenAI
from loguru import logger


class WhisperClient:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def transcribe(self, audio_bytes: bytes, filename: str = "voice.ogg") -> str:
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1], delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ru",
                )
            text = transcript.text.strip()
            logger.info(f"Transcribed audio: {text[:100]}")
            return text
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            raise
        finally:
            os.unlink(tmp_path)

    async def transcribe_from_path(self, path: str) -> str:
        with open(path, "rb") as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ru",
            )
        return transcript.text.strip()
