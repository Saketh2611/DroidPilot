from __future__ import annotations

import subprocess
from typing import Any


class ADBClient:
    def __init__(self, adb_path: str | None = None) -> None:
        self.adb_path = adb_path or "adb"

    def _run(self, *args: str) -> str:
        result = subprocess.run([self.adb_path, *args], capture_output=True, text=True, check=False)
        if result.returncode not in (0, 1):
            raise RuntimeError(f"ADB command failed: {' '.join(args)}")
        return result.stdout.strip()

    def devices(self) -> list[dict[str, Any]]:
        output = self._run("devices")
        devices: list[dict[str, Any]] = []
        lines = output.splitlines()[1:]
        for line in lines:
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                devices.append({"serial": parts[0], "status": parts[1]})
        return devices

    def shell(self, *args: str) -> str:
        return self._run("shell", *args)

    def screenshot(self, serial: str | None = None, path: str = "/sdcard/screenshot.png") -> str:
        if serial:
            self._run("-s", serial, "exec-out", "screencap", "-p")
        return path
