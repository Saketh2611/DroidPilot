from __future__ import annotations

import json
import time
from typing import Any

from groq import Groq

from ..actions.models import ActionModel, LaunchAppAction, PressAction, TapAction, TypeAction
from ..agent.base import Agent
from ..config import settings
from ..state.models import DeviceState


class GroqAgent(Agent):
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.groq_api_key
        self.model = model or settings.groq_model
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def next_action(self, goal: str, state: DeviceState):
        if not self.api_key or self.client is None:
            raise ValueError("GROQ_API_KEY is not configured")

        messages = [
            {
                "role": "system",
                "content": (
                    "You are DroidPilot. Return only a JSON object with an action schema. "
                    "Allowed action types: tap, type, press, launch_app, swipe, scroll, home, back, wait. "
                    "Never output shell commands or raw code."
                ),
            },
            {
                "role": "user",
                "content": json.dumps({
                    "goal": goal,
                    "device_info": state.device_info,
                    "current_package": state.current_package,
                    "ui_elements": [e.model_dump() for e in state.ui_elements],
                }),
            },
        ]

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0,
                    max_tokens=2048,
                )
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("Groq returned empty content")
                action_data = json.loads(content)
                return self._build_action(action_data)
            except Exception as exc:
                message = str(exc).lower()
                should_retry = attempt < 2 and (
                    "503" in str(exc)
                    or "unavailable" in message
                    or "rate" in message
                    or "overloaded" in message
                )
                if should_retry:
                    time.sleep(2)
                    continue
                raise

    def _build_action(self, data: dict[str, Any]) -> ActionModel:
        action_type = data.get("type")
        if action_type == "launch_app":
            return LaunchAppAction(package=data["package"]) 
        if action_type == "tap":
            target = data.get("target") or {}
            if "element_id" in target:
                return TapAction(element_id=int(target["element_id"]))
            return TapAction(target={"text": target.get("text"), "resource_id": target.get("resource_id")})
        if action_type == "type":
            return TypeAction(text=data["text"])
        if action_type == "press":
            return PressAction(key=data["key"])
        if action_type == "swipe":
            return ActionModel(type="swipe", direction=data["direction"])  # type: ignore[arg-type]
        if action_type == "scroll":
            return ActionModel(type="scroll", direction=data["direction"])  # type: ignore[arg-type]
        raise ValueError(f"Unsupported action type from Groq agent: {action_type}")
