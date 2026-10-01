"""
LeadFlow — Gemini AI Service
Wraps Google Gemini API with error handling and retry logic.
The model is configurable via settings.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Thin wrapper around Google Generative AI SDK.
    Model is configurable — change GEMINI_MODEL in .env to switch.
    """

    def __init__(self, api_key: str, model_name: str) -> None:
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Set it in your .env file."
            )
        self.api_key = api_key
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini model loaded: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                raise
        return self._model

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        max_retries: int = 2,
    ) -> str:
        """
        Generate a response from Gemini.
        Retries on rate limit errors.
        """
        model = self._load_model()

        full_prompt = prompt
        if system_instruction:
            full_prompt = f"{system_instruction}\n\n{prompt}"

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                response = model.generate_content(full_prompt)
                text = response.text.strip()
                return text
            except Exception as e:
                error_str = str(e).lower()
                if "rate" in error_str or "quota" in error_str:
                    wait = 2 ** attempt
                    logger.warning(
                        f"Gemini rate limit hit (attempt {attempt + 1}). "
                        f"Retrying in {wait}s..."
                    )
                    time.sleep(wait)
                    last_error = e
                elif "api_key" in error_str or "invalid" in error_str:
                    raise ValueError(
                        "Gemini API key is invalid. Check your .env configuration."
                    ) from e
                else:
                    raise RuntimeError(
                        f"Gemini API error: {e}"
                    ) from e

        raise RuntimeError(
            f"Gemini API failed after {max_retries + 1} attempts: {last_error}"
        )

    def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        max_retries: int = 2,
    ) -> dict:
        """Generate and parse JSON response from Gemini."""
        raw = self.generate(prompt, system_instruction, max_retries)

        text = raw.strip()
        import re

        # Match markdown block ```json ... ``` or ``` ... ```
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if fence_match:
            text = fence_match.group(1).strip()
        else:
            # Extract JSON object starting with { and ending with }
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                text = text[start:end + 1].strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Gemini returned invalid JSON: {e}\nRaw: {raw[:500]}")
            raise ValueError(
                f"AI response was not valid JSON. "
                f"This may be a temporary issue — please retry."
            ) from e


def create_gemini_service() -> GeminiService:
    """Factory using settings configuration."""
    from app.config import settings
    return GeminiService(
        api_key=settings.gemini_api_key,
        model_name=settings.gemini_model,
    )
