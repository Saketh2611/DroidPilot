from __future__ import annotations

import time
from typing import Any

from ..device.base import AndroidDevice
from .models import ActionModel


class ActionExecutor:
    def __init__(self, device: AndroidDevice):
        self.device = device

    def execute(self, action: ActionModel) -> dict[str, Any]:
        action_type = action.type
        if action_type == "launch_app":
            try:
                self.device.launch_app(action.package)
            except Exception as exc:
                return {
                    "status": "error",
                    "action": action_type,
                    "package": action.package,
                    "error": str(exc),
                }
            return {"status": "success", "action": action_type, "package": action.package}
        if action_type == "press":
            try:
                self.device.press(action.key)
            except Exception as exc:
                return {"status": "error", "action": action_type, "key": action.key, "error": str(exc)}
            return {"status": "success", "action": action_type, "key": action.key}
        if action_type == "tap":
            try:
                if action.element_id is not None:
                    self.device.tap_element(action.element_id)
                else:
                    self.device.tap(
                        action.target.model_dump(exclude_none=True) if action.target else {}
                    )
            except Exception as exc:
                return {
                    "status": "error",
                    "action": action_type,
                    "error": str(exc),
                    "target": (
                        action.target.model_dump(exclude_none=True)
                        if action.target
                        else {"element_id": action.element_id}
                    ),
                }
            return {
                "status": "success",
                "action": action_type,
                "target": (
                    action.target.model_dump(exclude_none=True)
                    if action.target
                    else {"element_id": action.element_id}
                ),
            }
        if action_type == "type":
            self.device.type(action.text)
            return {"status": "success", "action": action_type, "text": action.text}
        if action_type == "swipe":
            self.device.swipe(action.direction)
            return {"status": "success", "action": action_type, "direction": action.direction}
        if action_type == "scroll":
            self.device.scroll(action.direction)
            return {"status": "success", "action": action_type, "direction": action.direction}
        if action_type == "home":
            self.device.home()
            return {"status": "success", "action": action_type}
        if action_type == "back":
            self.device.back()
            return {"status": "success", "action": action_type}
        if action_type == "screenshot":
            self.device.screenshot()
            return {"status": "success", "action": action_type}
        if action_type == "wait":
            seconds = float(getattr(action, "seconds", 1.0) or 1.0)
            time.sleep(max(0.0, seconds))
            return {"status": "success", "action": action_type, "seconds": seconds}
        if action_type == "done":
            reason = getattr(action, "reason", "goal completed")
            return {"status": "completed", "action": action_type, "reason": reason}
        raise ValueError(f"Unsupported action: {action_type}")
