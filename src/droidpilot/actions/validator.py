from __future__ import annotations

from typing import Any

from .models import ACTION_MODELS, ActionModel


class ActionValidator:
    def validate(self, action: ActionModel | dict[str, Any]) -> ActionModel:
        if isinstance(action, ActionModel):
            return action
        if not isinstance(action, dict) or "type" not in action:
            raise ValueError("Action payload must be a dict with a 'type' field")

        action_type = action["type"]
        model_cls = ACTION_MODELS.get(action_type)
        if model_cls is None:
            raise ValueError(f"Unsupported action type: {action_type}")
        return model_cls.model_validate(action)
