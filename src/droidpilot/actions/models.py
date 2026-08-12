from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class TargetModel(BaseModel):
    text: str | None = None
    resource_id: str | None = None
    description: str | None = None
    element_id: int | None = None
    class_name: str | None = None


class ActionModel(BaseModel):
    type: str

    @model_validator(mode="after")
    def validate_type(self) -> "ActionModel":
        allowed = {
            "tap",
            "type",
            "swipe",
            "scroll",
            "press",
            "launch_app",
            "home",
            "back",
            "screenshot",
            "wait",
            "done",
        }
        if self.type not in allowed:
            raise ValueError(f"Unsupported action type: {self.type}")
        return self


class TapAction(ActionModel):
    type: Literal["tap"] = "tap"
    target: TargetModel | None = None
    element_id: int | None = None

    @model_validator(mode="after")
    def validate_target(self) -> "TapAction":
        if self.target is None and self.element_id is None:
            raise ValueError("Tap action needs target or element_id")
        if self.target is not None and self.target.text is not None and not self.target.text.strip():
            raise ValueError("Tap target text cannot be empty")
        return self


class TypeAction(ActionModel):
    type: Literal["type"] = "type"
    text: str = Field(..., min_length=1)


class SwipeAction(ActionModel):
    type: Literal["swipe"] = "swipe"
    direction: Literal["up", "down", "left", "right"]


class ScrollAction(ActionModel):
    type: Literal["scroll"] = "scroll"
    direction: Literal["up", "down", "left", "right"]


class PressAction(ActionModel):
    type: Literal["press"] = "press"
    key: str = Field(..., min_length=1)


class LaunchAppAction(ActionModel):
    type: Literal["launch_app"] = "launch_app"
    package: str = Field(..., min_length=1)


class HomeAction(ActionModel):
    type: Literal["home"] = "home"


class BackAction(ActionModel):
    type: Literal["back"] = "back"


class ScreenshotAction(ActionModel):
    type: Literal["screenshot"] = "screenshot"


class WaitAction(ActionModel):
    type: Literal["wait"] = "wait"
    seconds: float = 1.0


class DoneAction(ActionModel):
    type: Literal["done"] = "done"
    reason: str = "goal completed"


ACTION_MODELS = {
    "tap": TapAction,
    "type": TypeAction,
    "swipe": SwipeAction,
    "scroll": ScrollAction,
    "press": PressAction,
    "launch_app": LaunchAppAction,
    "home": HomeAction,
    "back": BackAction,
    "screenshot": ScreenshotAction,
    "wait": WaitAction,
    "done": DoneAction,
}
