from droidpilot.cli import normalize_shell_command


def test_normalize_shell_command_removes_wrapping_quotes():
    assert normalize_shell_command("'run \"open Chrome and search for saketh\"'") == 'run "open Chrome and search for saketh"'
    assert normalize_shell_command('run "open Chrome and search for saketh"') == 'run "open Chrome and search for saketh"'
