import base64
import json
import re
from typing import Any
from google import genai
from google.genai import types
from ..config import get_settings

settings = get_settings()


class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

    @property
    def enabled(self) -> bool:
        return self.client is not None

    async def generate_json(self, prompt: str, image_bytes: bytes | None = None, mime_type: str = "image/jpeg") -> dict[str, Any]:
        if not self.client:
            raise RuntimeError("Gemini is not configured.")

        contents: list[Any] = [prompt]
        if image_bytes:
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3,
        )

        response = await self.client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=contents,
            config=config,
        )
        text = (response.text or "").strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text)

    async def analyze_outfit(self, image_bytes: bytes, mime_type: str) -> str:
        if not self.client:
            return "Image analysis unavailable locally; use the supplied outfit color/style fields."

        response = await self.client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=[
                "Analyze this outfit image for a jewelry shopping assistant. Return a concise description of visible colors, overall style, neckline/neck area if visible, and jewelry styling considerations. Do not identify the person.",
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            ],
            config=types.GenerateContentConfig(temperature=0.2),
        )
        return (response.text or "").strip()


gemini_service = GeminiService()
