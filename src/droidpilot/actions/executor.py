from __future__ import annotations

from typing import Any

from ..device.base import AndroidDevice
from .models import ActionModel


class ActionExecutor:
    def __init__(self, device: AndroidDevice):
        self.device = device

    def execute(self, action: ActionModel) -> dict[str, Any]:
        action_type = action.type
        if action_type == "launch_app":
            self.device.launch_app(action.package)
            return {"status": "success", "action": action_type, "package": action.package}
        if action_type == "press":
            self.device.press(action.key)
            return {"status": "success", "action": action_type, "key": action.key}
        if action_type == "tap":
            if action.element_id is not None:
                self.device.tap_element(action.element_id)
            else:
                self.device.tap(action.target.model_dump(exclude_none=True) if action.target else {})
            return {"status": "success", "action": action_type, "target": action.target.model_dump(exclude_none=True) if action.target else {"element_id": action.element_id}}
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
            return {"status": "success", "action": action_type, "seconds": action.seconds}
        raise ValueError(f"Unsupported action: {action_type}")
