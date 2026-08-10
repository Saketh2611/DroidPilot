from droidpilot.actions.models import LaunchAppAction, PressAction, TapAction, TypeAction
from droidpilot.actions.validator import ActionValidator


def test_tap_action_is_valid():
    action = TapAction(target={"text": "Chrome"})
    assert action.type == "tap"
    assert action.target.text == "Chrome"


def test_type_action_is_valid():
    action = TypeAction(text="iQOO")
    assert action.type == "type"
    assert action.text == "iQOO"


def test_launch_app_action_is_valid():
    action = LaunchAppAction(package="com.android.chrome")
    assert action.type == "launch_app"
    assert action.package == "com.android.chrome"


def test_validator_rejects_invalid_action():
    validator = ActionValidator()
    try:
        validator.validate({"type": "tap", "target": {"text": ""}})
        raise AssertionError("Expected validation error")
    except ValueError:
        pass


def test_validator_accepts_press_action():
    validator = ActionValidator()
    action = validator.validate({"type": "press", "key": "enter"})
    assert isinstance(action, PressAction)
    assert action.key == "enter"
