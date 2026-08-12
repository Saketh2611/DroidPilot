from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .actions.executor import ActionExecutor
from .actions.models import ActionModel
from .actions.validator import ActionValidator
from .agent.gemini_agent import GeminiAgent
from .agent.mock_agent import MockAgent
from .config import settings
from .device.base import AndroidDevice
from .device.uiautomator import UIAutomatorDevice
from .session.history import SessionHistory
from .state.models import DeviceState, UIElement


@dataclass
class DroidPilotClient:
    device: AndroidDevice | None = None
    validator: ActionValidator = field(default_factory=ActionValidator)
    executor: ActionExecutor | None = None
    history: SessionHistory = field(default_factory=SessionHistory)
    agent: Any = None

    def __post_init__(self) -> None:
        if self.device is None:
            self.device = UIAutomatorDevice()
        if self.executor is None:
            self.executor = ActionExecutor(self.device)
        if self.agent is None:
            self.agent = GeminiAgent() if settings.is_llm_enabled else MockAgent()

    def connect(self, serial: str | None = None) -> dict[str, Any]:
        self.device.connect(serial=serial)
        return self.device.device_info()

    def disconnect(self) -> None:
        self.device.disconnect()

    def devices(self) -> list[dict[str, Any]]:
        return self.device.list_devices()

    def screenshot(self, path: str | None = None) -> str:
        return self.device.screenshot(path)

    def inspect(self) -> list[dict[str, Any]]:
        return self.device.inspect()

    def open_app(self, package: str) -> dict[str, Any]:
        return self.execute({"type": "launch_app", "package": package})

    def press(self, key: str) -> dict[str, Any]:
        return self.execute({"type": "press", "key": key})

    def tap(self, text: str | None = None, element_id: int | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"type": "tap"}
        if element_id is not None:
            payload["element_id"] = element_id
        elif text is not None:
            payload["target"] = {"text": text}
        return self.execute(payload)

    def type_text(self, text: str) -> dict[str, Any]:
        return self.execute({"type": "type", "text": text})

    def swipe(self, direction: str) -> dict[str, Any]:
        return self.execute({"type": "swipe", "direction": direction})

    def scroll(self, direction: str) -> dict[str, Any]:
        return self.execute({"type": "scroll", "direction": direction})

    def execute(self, action_data: dict[str, Any] | ActionModel) -> dict[str, Any]:
        validated = self.validator.validate(action_data)
        result = self.executor.execute(validated)
        self.history.record(action=validated.model_dump(), result=result)
        return result

    def _build_state(self, raw_state: dict[str, Any]) -> DeviceState:
        ui_elements = [
            UIElement(
                element_id=element.get("element_id", i),
                text=element.get("text"),
                resource_id=element.get("resource_id"),
                description=element.get("description"),
                class_name=element.get("class_name"),
                clickable=bool(element.get("clickable")),
                bounds=tuple(element.get("bounds")) if element.get("bounds") else None,
                attributes=element.get("attributes", {}),
            )
            for i, element in enumerate(raw_state.get("ui_elements", []), start=1)
        ]
        return DeviceState(
            screenshot=raw_state.get("screenshot"),
            ui_elements=ui_elements,
            current_package=raw_state.get("current_package"),
            device_info=raw_state.get("device_info", {}),
        )

    def _sanitize_action(self, action: ActionModel, state: DeviceState) -> ActionModel:
        """Rewrite invalid element_id taps into selector taps when possible."""
        if action.type != "tap" or action.element_id is None:
            return action

        max_id = len(state.ui_elements)
        if 1 <= action.element_id <= max_id:
            return action

        # Out-of-range id from the model: try target fields, otherwise error later.
        if action.target is not None and any(
            [
                action.target.text,
                action.target.resource_id,
                action.target.description,
            ]
        ):
            return action.model_copy(update={"element_id": None})
        raise ValueError(
            f"Element {action.element_id} does not exist (available: 1-{max_id})"
        )

    def run_goal(self, goal: str, max_steps: int = 20) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        recent: list[dict[str, Any]] = []

        for _ in range(max_steps):
            raw_state = self.device.observe()
            state = self._build_state(raw_state)

            try:
                action = self.agent.next_action(goal=goal, state=state, history=recent)
                validated = self.validator.validate(action)
                validated = self._sanitize_action(validated, state)
                result = self.executor.execute(validated)
            except Exception as exc:
                result = {"status": "error", "error": str(exc)}
                self.history.record(action={"type": "error"}, result=result)
                results.append(result)
                recent.append({"action": {"type": "error"}, "result": result})
                # Transient model/device errors should not kill the whole goal loop.
                if len(recent) >= 3 and all(r.get("result", {}).get("status") == "error" for r in recent[-3:]):
                    break
                continue

            self.history.record(action=validated.model_dump(), result=result)
            results.append(result)
            recent.append({"action": validated.model_dump(exclude_none=True), "result": result})

            if result.get("status") == "completed":
                break
        return results
