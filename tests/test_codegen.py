from droidpilot.session.history import SessionHistory
from droidpilot.session.codegen import generate_python_code


def test_generate_python_code_from_history():
    history = SessionHistory()
    history.record(action={"type": "launch_app", "package": "com.android.chrome"}, result={"status": "success"})
    history.record(action={"type": "type", "text": "iQOO"}, result={"status": "success"})

    code = generate_python_code(history)
    assert "from droidpilot import DroidPilotClient" in code
    assert "client.open_app(\"com.android.chrome\")" in code
    assert "client.type_text(\"iQOO\")" in code
