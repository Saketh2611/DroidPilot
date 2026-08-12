from __future__ import annotations

import time
from typing import Any

from groq import Groq

from ..agent.action_builder import build_action_from_llm
from ..agent.base import Agent
from ..agent.json_utils import extract_json_object
from ..agent.prompts import SYSTEM_PROMPT, build_user_prompt
from ..config import settings
from ..state.models import DeviceState


class GroqAgent(Agent):
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.groq_api_key
        self.model = model or settings.groq_model
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def next_action(self, goal: str, state: DeviceState, history: list[dict[str, Any]] | None = None):
        if not self.api_key or self.client is None:
            raise ValueError("GROQ_API_KEY is not configured")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_user_prompt(goal=goal, state=state, history=history),
            },
        ]

        last_error: Exception | None = None
        for attempt in range(4):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0,
                    max_tokens=1024,
                    response_format={"type": "json_object"},
                )
                content = response.choices[0].message.content
                action_data = extract_json_object(content or "")
                return build_action_from_llm(action_data)
            except Exception as exc:
                last_error = exc
                message = str(exc).lower()
                should_retry = attempt < 3 and (
                    "503" in str(exc)
                    or "unavailable" in message
                    or "rate" in message
                    or "overloaded" in message
                    or "empty content" in message
                    or "did not return json" in message
                    or "expecting value" in message
                    or "json" in message
                )
                if should_retry:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise
        raise last_error or ValueError("Groq agent failed without a specific error")
