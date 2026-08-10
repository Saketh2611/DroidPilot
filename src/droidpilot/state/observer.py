from __future__ import annotations

from typing import Any

from ..device.base import AndroidDevice
from .models import DeviceState


class StateObserver:
    def __init__(self, device: AndroidDevice):
        self.device = device

    def observe(self) -> DeviceState:
        data = self.device.observe()
        ui_elements = data.get("ui_elements", [])
        return DeviceState(
            screenshot=data.get("screenshot"),
            ui_elements=[
                type("ElementProxy", (), element)() for element in ui_elements
            ],
            current_package=data.get("current_package"),
            device_info=data.get("device_info", {}),
        )
