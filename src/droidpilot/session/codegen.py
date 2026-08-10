from __future__ import annotations

from typing import Any

from .history import SessionHistory


def generate_python_code(history: SessionHistory) -> str:
    lines = [
        "from droidpilot import DroidPilotClient",
        "",
        "client = DroidPilotClient()",
    ]
    for entry in history.entries:
        action = entry.get("action", {})
        action_type = action.get("type")
        if action_type == "launch_app":
            package = action.get("package", "")
            lines.append(f'client.open_app("{package}")')
        elif action_type == "type":
            text = action.get("text", "")
            lines.append(f'client.type_text("{text}")')
        elif action_type == "press":
            key = action.get("key", "")
            lines.append(f'client.press("{key}")')
        elif action_type == "tap":
            target = action.get("target") or {}
            if target.get("text"):
                lines.append(f'client.tap(text="{target["text"]}")')
            elif target.get("resource_id"):
                lines.append(f'client.tap(element_id=None)')
        elif action_type == "swipe":
            direction = action.get("direction", "up")
            lines.append(f'client.swipe("{direction}")')
    return "\n".join(lines) + "\n"
