from droidpilot.agent.action_builder import build_action_from_llm
from droidpilot.agent.json_utils import extract_json_object
from droidpilot.actions.models import DoneAction, HomeAction, TapAction
from droidpilot.actions.validator import ActionValidator


def test_extract_json_object_from_fence():
    text = """```json
{"type":"home"}
```"""
    data = extract_json_object(text)
    assert data["type"] == "home"


def test_extract_json_object_from_prose():
    text = 'Next step: {"type":"tap","element_id":3} thanks'
    data = extract_json_object(text)
    assert data["element_id"] == 3


def test_build_action_done_aliases():
    action = build_action_from_llm({"type": "completed", "reason": "done"})
    assert isinstance(action, DoneAction)
    assert action.reason == "done"


def test_build_action_home_and_tap():
    assert isinstance(build_action_from_llm({"type": "home"}), HomeAction)
    action = build_action_from_llm({"type": "tap", "element_id": 12})
    assert isinstance(action, TapAction)
    assert action.element_id == 12


def test_validator_accepts_done():
    validator = ActionValidator()
    action = validator.validate({"type": "done", "reason": "ok"})
    assert isinstance(action, DoneAction)
