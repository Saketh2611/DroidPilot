from __future__ import annotations

from ..actions.models import LaunchAppAction, TapAction, TypeAction, PressAction
from ..agent.base import Agent
from ..state.models import DeviceState


class MockAgent(Agent):
    def next_action(self, goal: str, state: DeviceState):
        lowered = goal.lower()
        if "chrome" in lowered and not state.current_package:
            return LaunchAppAction(package="com.android.chrome")

        if "chrome" in lowered and state.current_package == "com.android.chrome":
            has_url_bar = any(
                element.resource_id and "url_bar" in element.resource_id for element in state.ui_elements
            )
            if has_url_bar:
                return TypeAction(text="iQOO")

            for element in state.ui_elements:
                if element.resource_id and "url_bar" in element.resource_id:
                    return TapAction(target={"resource_id": element.resource_id})
                if element.text and "search" in element.text.lower():
                    return TapAction(target={"text": element.text})
            if any(element.class_name and "EditText" in element.class_name for element in state.ui_elements):
                return TypeAction(text="iQOO")

        if "iqoo" in lowered and state.current_package == "com.android.chrome":
            return TypeAction(text="iQOO")
        return PressAction(key="enter")
