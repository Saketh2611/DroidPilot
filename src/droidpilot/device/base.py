from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AndroidDevice(ABC):
    @abstractmethod
    def connect(self, serial: str | None = None) -> dict[str, Any]:
        ...

    @abstractmethod
    def disconnect(self) -> None:
        ...

    @abstractmethod
    def list_devices(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    def screenshot(self, path: str | None = None) -> str:
        ...

    @abstractmethod
    def inspect(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    def tap(self, target: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def tap_element(self, element_id: int) -> dict[str, Any]:
        ...

    @abstractmethod
    def type(self, text: str) -> dict[str, Any]:
        ...

    @abstractmethod
    def swipe(self, direction: str) -> dict[str, Any]:
        ...

    @abstractmethod
    def scroll(self, direction: str) -> dict[str, Any]:
        ...

    @abstractmethod
    def press(self, key: str) -> dict[str, Any]:
        ...

    @abstractmethod
    def launch_app(self, package: str) -> dict[str, Any]:
        ...
        
    @abstractmethod
    def dial(self, number: str) -> dict[str, Any]:
        ...

    @abstractmethod
    def home(self) -> dict[str, Any]:
        ...

    @abstractmethod
    def back(self) -> dict[str, Any]:
        ...

    @abstractmethod
    def current_package(self) -> str | None:
        ...

    @abstractmethod
    def device_info(self) -> dict[str, Any]:
        ...

    @abstractmethod
    def observe(self) -> dict[str, Any]:
        ...
