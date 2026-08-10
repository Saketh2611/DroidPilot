from droidpilot.agent.mock_agent import MockAgent
from droidpilot.state.models import DeviceState, UIElement


def test_mock_agent_opens_chrome_for_search_goal():
    agent = MockAgent()
    state = DeviceState(
        screenshot=None,
        ui_elements=[],
        current_package=None,
        device_info={"model": "test"},
    )
    action = agent.next_action(goal="Open Chrome and search for iQOO", state=state)
    assert action.type == "launch_app"
    assert action.package == "com.android.chrome"


def test_mock_agent_types_after_url_bar_present():
    agent = MockAgent()
    state = DeviceState(
        screenshot=None,
        ui_elements=[
            UIElement(element_id=1, text="Google", resource_id="com.android.chrome:id/url_bar", class_name="EditText", clickable=True, bounds=(0, 0, 100, 50)),
        ],
        current_package="com.android.chrome",
        device_info={"model": "test"},
    )
    action = agent.next_action(goal="Open Chrome and search for iQOO", state=state)
    assert action.type == "type"
    assert action.text == "iQOO"
