from __future__ import annotations

from typing import Any

from ..actions.models import (
    ActionModel,
    BackAction,
    DoneAction,
    HomeAction,
    LaunchAppAction,
    PressAction,
    ScrollAction,
    SwipeAction,
    TapAction,
    TypeAction,
    WaitAction,
)


def build_action_from_llm(data: dict[str, Any]) -> ActionModel:
    """Normalize LLM JSON into a typed ActionModel."""
    normalized = dict(data)
    if "type" not in normalized and "action" in normalized:
        normalized["type"] = normalized.pop("action")

    action_type = normalized.get("type")
    if action_type in {"done", "complete", "completed", "finish", "finished"}:
        return DoneAction(reason=str(normalized.get("reason") or "goal completed"))
    if action_type == "launch_app":
        package = normalized.get("package") or normalized.get("app")
        if not package:
            raise ValueError("launch_app requires package")
        return LaunchAppAction(package=str(package))
    if action_type == "tap":
        target = normalized.get("target") or {}
        element_id = normalized.get("element_id")
        if element_id is None and isinstance(target, dict):
            element_id = target.get("element_id")
        if element_id is not None:
            return TapAction(element_id=int(element_id), target=target if target else None)
        return TapAction(
            target={
                "text": target.get("text"),
                "resource_id": target.get("resource_id"),
                "description": target.get("description"),
                "class_name": target.get("class_name"),
            }
        )
    if action_type == "type":
        return TypeAction(text=str(normalized["text"]))
    if action_type == "press":
        return PressAction(key=str(normalized["key"]))
    if action_type == "swipe":
        return SwipeAction(direction=normalized["direction"])
    if action_type == "scroll":
        return ScrollAction(direction=normalized["direction"])
    if action_type == "home":
        return HomeAction()
    if action_type == "back":
        return BackAction()
    if action_type == "wait":
        seconds = normalized.get("seconds", 1.0)
        return WaitAction(seconds=float(seconds))
    raise ValueError(f"Unsupported action type from agent: {action_type}")
