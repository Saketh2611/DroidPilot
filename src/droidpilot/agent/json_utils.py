from __future__ import annotations

import json
import re
from typing import Any


def extract_json_object(text: str) -> dict[str, Any]:
    """Parse a JSON object from model output, tolerating markdown fences and prose."""
    if text is None:
        raise ValueError("Model returned empty content")

    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Model returned empty content")

    fence_match = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fence_match:
        cleaned = fence_match.group(1).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            raise ValueError(f"Model did not return JSON: {cleaned[:200]!r}")
        data = json.loads(cleaned[start : end + 1])

    if not isinstance(data, dict):
        raise ValueError("Model JSON must be an object")
    return data
