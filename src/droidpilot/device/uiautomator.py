from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
from typing import Any

import uiautomator2 as u2

from .adb import ADBClient
from .base import AndroidDevice


def parse_hierarchy_xml(xml_content: str) -> list[dict[str, Any]]:
    root = ET.fromstring(xml_content)
    nodes: list[dict[str, Any]] = []

    def normalize_name(name: str) -> str:
        if name == "resource-id":
            return "resource_id"
        if name == "content-desc":
            return "content_description"
        if name == "class":
            return "class_name"
        return name.replace("-", "_")

    def parse_bounds(value: str | None) -> tuple[int, int, int, int] | None:
        if not value:
            return None

        numbers = re.findall(r"-?\d+", value)
        if len(numbers) < 4:
            return None

        left, top, right, bottom = (int(part) for part in numbers[:4])
        return (left, top, right, bottom)

    def walk(element: ET.Element) -> None:
        if element.tag == "hierarchy":
            for child in element:
                walk(child)
            return

        if element.tag != "node":
            for child in element:
                walk(child)
            return

        attrs: dict[str, Any] = {}
        for key, value in element.attrib.items():
            normalized = normalize_name(key)
            attrs[normalized] = value

        is_clickable = str(attrs.get("clickable", "false")).lower() == "true"
        has_identity = bool(
            (attrs.get("text") or "").strip()
            or (attrs.get("resource_id") or "").strip()
            or (attrs.get("content_description") or "").strip()
        )
        is_container = len(element) > 0 and not has_identity and not is_clickable

        bounds = parse_bounds(attrs.get("bounds"))
        node = {
            "text": attrs.get("text", ""),
            "resource_id": attrs.get("resource_id"),
            "description": attrs.get("content_description"),
            "class_name": attrs.get("class_name"),
            "clickable": is_clickable,
            "bounds": bounds,
            "attributes": attrs,
        }
        if not is_container:
            nodes.append(node)
        for child in element:
            walk(child)

    for child in root:
        walk(child)
    return nodes


class UIAutomatorDevice(AndroidDevice):
    def __init__(self, serial: str | None = None, adb: ADBClient | None = None) -> None:
        self.serial = serial
        self.adb = adb or ADBClient()
        self._device: u2.Device | None = None

    def connect(self, serial: str | None = None) -> dict[str, Any]:
        self.serial = serial or self.serial
        if self.serial:
            self._device = u2.connect(self.serial)
        else:
            self._device = u2.connect()
        return self.device_info()

    def disconnect(self) -> None:
        if self._device is not None:
            self._device = None

    def _ensure_connected(self) -> u2.Device:
        if self._device is None:
            self.connect()
        return self._device

    def list_devices(self) -> list[dict[str, Any]]:
        raw = self.adb.devices()
        return raw

    def screenshot(self, path: str | None = None) -> str:
        device = self._ensure_connected()
        screenshot_path = path or os.path.join(os.getcwd(), "droidpilot_screenshot.png")
        device.screenshot(screenshot_path)
        return screenshot_path

    def inspect(self) -> list[dict[str, Any]]:
        device = self._ensure_connected()
        hierarchy = device.dump_hierarchy()
        parsed = parse_hierarchy_xml(hierarchy)
        result: list[dict[str, Any]] = []
        for index, node in enumerate(parsed, start=1):
            text = node.get("text") or node.get("description") or node.get("resource_id")
            result.append(
                {
                    "element_id": index,
                    "text": text,
                    "resource_id": node.get("resource_id"),
                    "description": node.get("description"),
                    "class_name": node.get("class_name"),
                    "clickable": bool(node.get("clickable")),
                    "bounds": node.get("bounds"),
                    "attributes": node.get("attributes", {}),
                }
            )
        return result

    def tap(self, target: dict[str, Any]) -> dict[str, Any]:
        device = self._ensure_connected()
        text = target.get("text")
        resource_id = target.get("resource_id")
        description = target.get("description")
        if resource_id:
            device(resourceId=resource_id).click()
            return {"status": "success", "target": {"resource_id": resource_id}}
        if description:
            device(description=description).click()
            return {"status": "success", "target": {"description": description}}
        if text:
            device(text=text).click()
            return {"status": "success", "target": {"text": text}}
        raise ValueError("No valid tap target was provided")

    def tap_element(self, element_id: int) -> dict[str, Any]:
        device = self._ensure_connected()
        elements = parse_hierarchy_xml(device.dump_hierarchy())
        if element_id < 1 or element_id > len(elements):
            raise ValueError(f"Element {element_id} does not exist")
        node = elements[element_id - 1]
        bounds = node.get("bounds")
        if bounds:
            x1, y1, x2, y2 = bounds
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            device.click(center_x, center_y)
            return {"status": "success", "element_id": element_id, "bounds": bounds}
        raise ValueError(f"Element {element_id} has no usable bounds")

    def type(self, text: str) -> dict[str, Any]:
        device = self._ensure_connected()
        if hasattr(device, "set_fastinput_ime"):
            device.set_fastinput_ime(False)
        if hasattr(device, "send_keys"):
            device.send_keys(text)
        elif hasattr(device, "set_text"):
            device.set_text(text)
        else:
            raise AttributeError("Connected device does not support text input")
        return {"status": "success", "text": text}

    def swipe(self, direction: str) -> dict[str, Any]:
        device = self._ensure_connected()
        width, height = device.info["displayWidth"], device.info["displayHeight"]
        if direction == "up":
            device.swipe(width // 2, height * 3 // 4, width // 2, height // 4)
        elif direction == "down":
            device.swipe(width // 2, height // 4, width // 2, height * 3 // 4)
        elif direction == "left":
            device.swipe(width * 3 // 4, height // 2, width // 4, height // 2)
        elif direction == "right":
            device.swipe(width // 4, height // 2, width * 3 // 4, height // 2)
        else:
            raise ValueError(f"Unsupported swipe direction: {direction}")
        return {"status": "success", "direction": direction}

    def scroll(self, direction: str) -> dict[str, Any]:
        device = self._ensure_connected()
        if direction == "up":
            device.swipe_points([(0.5, 0.8), (0.5, 0.2)])
        elif direction == "down":
            device.swipe_points([(0.5, 0.2), (0.5, 0.8)])
        else:
            raise ValueError(f"Unsupported scroll direction: {direction}")
        return {"status": "success", "direction": direction}

    def press(self, key: str) -> dict[str, Any]:
        device = self._ensure_connected()
        device.press(key)
        return {"status": "success", "key": key}

    def launch_app(self, package: str) -> dict[str, Any]:
        device = self._ensure_connected()
        device.app_start(package)
        return {"status": "success", "package": package}

    def home(self) -> dict[str, Any]:
        device = self._ensure_connected()
        device.press.home()
        return {"status": "success"}

    def back(self) -> dict[str, Any]:
        device = self._ensure_connected()
        device.press.back()
        return {"status": "success"}

    def current_package(self) -> str | None:
        device = self._ensure_connected()
        return device.app_current().get("package") if hasattr(device, "app_current") else None

    def device_info(self) -> dict[str, Any]:
        device = self._ensure_connected()
        info = device.info
        return {
            "serial": self.serial or info.get("serial"),
            "manufacturer": info.get("manufacturer"),
            "model": info.get("model"),
            "device": info.get("device"),
            "android_version": info.get("version"),
            "screen": info.get("displayWidth"),
            "resolution": f"{info.get('displayWidth')}x{info.get('displayHeight')}",
        }

    def observe(self) -> dict[str, Any]:
        device = self._ensure_connected()
        return {
            "screenshot": self.screenshot(),
            "ui_elements": self.inspect(),
            "current_package": self.current_package(),
            "device_info": self.device_info(),
        }
