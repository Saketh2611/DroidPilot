from __future__ import annotations

from abc import ABC, abstractmethod

from ..state.models import DeviceState


class Agent(ABC):
    @abstractmethod
    def next_action(self, goal: str, state: DeviceState) -> dict:
        ...
