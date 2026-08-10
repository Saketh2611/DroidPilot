from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class UIElement(BaseModel):
    element_id: int
    text: str | None = None
    resource_id: str | None = None
    description: str | None = None
    class_name: str | None = None
    clickable: bool = False
    bounds: tuple[int, int, int, int] | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class DeviceState(BaseModel):
    screenshot: str | None = None
    ui_elements: list[UIElement] = Field(default_factory=list)
    current_package: str | None = None
    device_info: dict[str, Any] = Field(default_factory=dict)
