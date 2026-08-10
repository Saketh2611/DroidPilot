from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SessionHistory:
    entries: list[dict[str, Any]] = field(default_factory=list)

    def record(self, action: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "result": result,
        }
        self.entries.append(entry)
        return entry

    def list(self) -> list[dict[str, Any]]:
        return list(self.entries)

    def export(self, path: str) -> str:
        import json

        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.entries, handle, indent=2)
        return path
