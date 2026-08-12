from __future__ import annotations

import time
from typing import Any

from google import genai
from google.genai import types

from ..agent.action_builder import build_action_from_llm
from ..agent.base import Agent
from ..agent.json_utils import extract_json_object
from ..agent.prompts import SYSTEM_PROMPT, build_user_prompt
from ..config import settings
from ..state.models import DeviceState


class GeminiAgent(Agent):
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.google_api_key
        self.model = model or settings.gemini_model
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def next_action(self, goal: str, state: DeviceState, history: list[dict[str, Any]] | None = None):
        if not self.api_key or self.client is None:
            raise ValueError("GOOGLE_API_KEY is not configured")

        prompt = build_user_prompt(goal=goal, state=state, history=history)

        last_error: Exception | None = None
        for attempt in range(4):
            try:
                config_kwargs: dict[str, Any] = {
                    "temperature": 0,
                    "max_output_tokens": 1024,
                }
                # Prefer JSON mode; fall back if the model rejects mime type.
                if attempt < 2:
                    config_kwargs["response_mime_type"] = "application/json"

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=f"{SYSTEM_PROMPT}\n\n{prompt}",
                    config=types.GenerateContentConfig(**config_kwargs),
                )
                text = self._extract_text(response)
                action_data = extract_json_object(text)
                return build_action_from_llm(action_data)
            except Exception as exc:
                last_error = exc
                message = str(exc).lower()
                should_retry = attempt < 3 and (
                    "503" in str(exc)
                    or "unavailable" in message
                    or "rate" in message
                    or "overloaded" in message
                    or "timeout" in message
                    or "empty content" in message
                    or "did not return json" in message
                    or "expecting value" in message
                    or "json" in message
                    or "mime" in message
                    or "invalid" in message
                )
                if should_retry:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise
        raise last_error or ValueError("Gemini agent failed without a specific error")

    def _extract_text(self, response: Any) -> str:
        text = getattr(response, "text", None)
        if isinstance(text, str) and text.strip():
            return text

        candidates = getattr(response, "candidates", None) or []
        chunks: list[str] = []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None) or []
            for part in parts:
                part_text = getattr(part, "text", None)
                if part_text:
                    chunks.append(part_text)
        combined = "\n".join(chunks).strip()
        if combined:
            return combined

        finish_reasons = [
            str(getattr(candidate, "finish_reason", ""))
            for candidate in candidates
        ]
        raise ValueError(
            "Gemini returned empty content"
            + (f" (finish_reason={finish_reasons})" if finish_reasons else "")
        )
