from __future__ import annotations

import json
import time
from typing import Any

from google import genai
from google.genai import types

from ..actions.models import ActionModel, LaunchAppAction, PressAction, TapAction, TypeAction
from ..agent.base import Agent
from ..config import settings
from ..state.models import DeviceState


class GeminiAgent(Agent):
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.google_api_key
        self.model = model or settings.gemini_model
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def next_action(self, goal: str, state: DeviceState):
        if not self.api_key or self.client is None:
            raise ValueError("GOOGLE_API_KEY is not configured")

        prompt = json.dumps({
            "goal": goal,
            "device_info": state.device_info,
            "current_package": state.current_package,
            "ui_elements": [e.model_dump() for e in state.ui_elements],
        })

        system = (
            "You are DroidPilot. Return only a JSON object with an action schema. "
            "Allowed action types: tap, type, press, launch_app, swipe, scroll, home, back, wait. "
            "Never output shell commands or raw code."
        )

        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=system + "\n\n" + prompt,
                    config=types.GenerateContentConfig(
                        temperature=0,
                        max_output_tokens=2048,
                    ),
                )
                text = getattr(response, "text", "")
                if not text:
                    raise ValueError("Gemini returned empty content")
                action_data = json.loads(text)
                return self._build_action(action_data)
            except Exception as exc:
                message = str(exc).lower()
                should_retry = attempt < 2 and (
                    "503" in str(exc)
                    or "unavailable" in message
                    or "rate" in message
                    or "overloaded" in message
                    or "timeout" in message
                )
                if should_retry:
                    time.sleep(2)
                    continue
                raise

    def _build_action(self, data: dict[str, Any]) -> ActionModel:
        normalized = dict(data)
        if "type" not in normalized and "action" in normalized:
            normalized["type"] = normalized["action"]

        action_type = normalized.get("type")
        if action_type == "launch_app":
            return LaunchAppAction(package=normalized["package"])
        if action_type == "tap":
            target = normalized.get("target") or {}
            element_id = normalized.get("element_id")
            if element_id is not None:
                return TapAction(element_id=int(element_id))
            if "element_id" in target:
                return TapAction(element_id=int(target["element_id"]))
            return TapAction(target={"text": target.get("text"), "resource_id": target.get("resource_id")})
        if action_type == "type":
            return TypeAction(text=normalized["text"])
        if action_type == "press":
            return PressAction(key=normalized["key"])
        if action_type == "swipe":
            return ActionModel(type="swipe", direction=normalized["direction"])  # type: ignore[arg-type]
        if action_type == "scroll":
            return ActionModel(type="scroll", direction=normalized["direction"])  # type: ignore[arg-type]
        raise ValueError(f"Unsupported action type from Gemini agent: {action_type}")
