from __future__ import annotations

import json
from typing import Any

from ..state.models import DeviceState, UIElement

SYSTEM_PROMPT = """You are DroidPilot, an Android UI automation agent.
You control a real phone through structured actions that the runtime maps to ADB/uiautomator2.
Return ONLY one JSON object for the next single step. No markdown, no prose, no shell commands.

Allowed actions:
{"type":"launch_app","package":"<android package name>"}
{"type":"tap","element_id":<id from ui_elements>}
{"type":"tap","target":{"text":"<visible text>"}}
{"type":"tap","target":{"resource_id":"<id>"}}
{"type":"tap","target":{"description":"<content-desc>"}}
{"type":"type","text":"<text to type into focused field>"}
{"type":"press","key":"enter|back|home|recent|delete"}
{"type":"swipe","direction":"up|down|left|right"}
{"type":"scroll","direction":"up|down"}
{"type":"home"}
{"type":"back"}
{"type":"wait","seconds":1.0}
{"type":"done","reason":"goal completed"}

Rules:
1. Handle ANY Android task: browser, calculator, settings, messages, camera, files, play store, etc.
2. Prefer launch_app when opening a known app. Otherwise press home, then tap the app icon by text/description.
3. ONLY use element_id values that appear in the provided ui_elements list.
4. Prefer unique text / content-desc / resource_id taps when available; otherwise use element_id.
5. One action per response. Re-observe happens after every action.
6. When the user goal is fully achieved, return {"type":"done","reason":"..."}.
7. If the UI is loading or transitioning, return wait.
8. Never invent UI text or element_ids that are not present.

Common packages (use when relevant; device may differ):
- Chrome: com.android.chrome
- Calculator: com.google.android.calculator or com.android.calculator2 or com.coloros.calculator
- Settings: com.android.settings
- Messages: com.google.android.apps.messaging
- Camera: com.android.camera / com.android.camera2
- Play Store: com.android.vending
"""


def _compact_element(element: UIElement) -> dict[str, Any]:
    payload: dict[str, Any] = {"element_id": element.element_id}
    if element.text:
        payload["text"] = element.text
    if element.resource_id:
        payload["resource_id"] = element.resource_id
    if element.description:
        payload["description"] = element.description
    if element.class_name:
        payload["class_name"] = element.class_name
    payload["clickable"] = element.clickable
    if element.bounds:
        payload["bounds"] = list(element.bounds)
    return payload


def build_user_prompt(
    goal: str,
    state: DeviceState,
    history: list[dict[str, Any]] | None = None,
    max_elements: int = 120,
) -> str:
    elements = list(state.ui_elements)
    # Prefer interactive / labeled nodes so the model sees useful targets first.
    ranked = sorted(
        elements,
        key=lambda e: (
            0 if e.clickable else 1,
            0 if (e.text or e.description or e.resource_id) else 1,
            e.element_id,
        ),
    )
    compact = [_compact_element(e) for e in ranked[:max_elements]]
    payload = {
        "goal": goal,
        "current_package": state.current_package,
        "device_info": state.device_info,
        "ui_element_count": len(elements),
        "ui_elements": compact,
        "recent_actions": (history or [])[-8:],
    }
    return json.dumps(payload, ensure_ascii=False)
