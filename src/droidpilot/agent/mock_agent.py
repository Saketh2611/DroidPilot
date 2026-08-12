from __future__ import annotations

from ..actions.models import DoneAction, HomeAction, LaunchAppAction, PressAction, TapAction, TypeAction, WaitAction
from ..agent.base import Agent
from ..state.models import DeviceState


class MockAgent(Agent):
    """Deterministic fallback used when no LLM key is configured."""

    def next_action(self, goal: str, state: DeviceState, history: list | None = None):
        lowered = goal.lower()
        package = (state.current_package or "").lower()

        if any(word in lowered for word in ("calculator", "calc")):
            calc_packages = {
                "com.google.android.calculator",
                "com.android.calculator2",
                "com.coloros.calculator",
                "com.sec.android.app.popupcalculator",
            }
            if package not in calc_packages and "calculator" not in package:
                return LaunchAppAction(package="com.google.android.calculator")
            for element in state.ui_elements:
                label = (element.text or element.description or "").strip()
                if label and label in {"1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "+", "-", "×", "÷", "=", "."}:
                    if any(token in lowered for token in (label.lower(),)):
                        return TapAction(element_id=element.element_id)
            return DoneAction(reason="Calculator is open")

        if "settings" in lowered:
            if "settings" not in package:
                return LaunchAppAction(package="com.android.settings")
            return DoneAction(reason="Settings is open")

        if "chrome" in lowered or "search for" in lowered or "google" in lowered:
            if "chrome" not in package:
                return LaunchAppAction(package="com.android.chrome")

            has_url_bar = any(
                element.resource_id and "url_bar" in element.resource_id for element in state.ui_elements
            )
            query = goal
            for prefix in ("open chrome and search for", "search for", "google"):
                if prefix in lowered:
                    query = goal[lowered.index(prefix) + len(prefix) :].strip(" \"'")
                    break

            if has_url_bar:
                # If we already typed recently, press enter; otherwise type the query.
                recent = history or []
                if recent and recent[-1].get("action", {}).get("type") == "type":
                    return PressAction(key="enter")
                return TypeAction(text=query or "search")

            for element in state.ui_elements:
                if element.resource_id and "url_bar" in element.resource_id:
                    return TapAction(target={"resource_id": element.resource_id})
                if element.text and "search" in element.text.lower():
                    return TapAction(target={"text": element.text})
            if any(element.class_name and "EditText" in element.class_name for element in state.ui_elements):
                return TypeAction(text=query or "search")
            return WaitAction(seconds=1.0)

        if "home" in lowered:
            return HomeAction()

        # Generic: try launching by simple app name tap on launcher.
        if lowered.startswith("open "):
            app_name = goal[5:].strip(" \"'")
            for element in state.ui_elements:
                label = (element.text or element.description or "").strip()
                if label and app_name.lower() in label.lower():
                    return TapAction(element_id=element.element_id)
            return HomeAction()

        return DoneAction(reason="No mock heuristic matched; mark complete")
