from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .client import DroidPilotClient
from .config import settings

app = typer.Typer(help="DroidPilot: AI-assisted Android automation CLI")
console = Console()


def normalize_shell_command(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    return value


@app.callback()
def callback() -> None:
    """DroidPilot CLI."""


@app.command("config")
def config() -> None:
    table = Table(title="DroidPilot configuration")
    table.add_column("Setting")
    table.add_column("Value")
    table.add_row("provider", settings.provider)
    table.add_row("gemini_model", settings.gemini_model)
    table.add_row("google_api_key", "set" if settings.google_api_key else "not set")
    table.add_row("max_steps", str(settings.max_steps))
    table.add_row("device_id", settings.device_id or "not set")
    table.add_row("screenshot_dir", settings.screenshot_dir)
    console.print(table)


@app.command("devices")
def devices() -> None:
    client = DroidPilotClient()
    devices_found = client.devices()
    console.print("[bold]DroidPilot[/bold]\n[cyan]Connected devices[/cyan]")
    if not devices_found:
        console.print("No devices found.")
        return
    for device in devices_found:
        serial = device.get("serial", "unknown")
        console.print(f"● {serial}")
        console.print(f"  Status: {device.get('status', 'unknown')}")


@app.command("connect")
def connect(serial: str | None = None) -> None:
    client = DroidPilotClient()
    info = client.connect(serial)
    console.print("[green]Connected successfully[/green]")
    console.print(info)


@app.command("screenshot")
def screenshot(path: str | None = None) -> None:
    client = DroidPilotClient()
    saved = client.screenshot(path)
    console.print(f"[green]Screenshot saved to {saved}[/green]")


@app.command("inspect")
def inspect() -> None:
    client = DroidPilotClient()
    elements = client.inspect()
    for idx, element in enumerate(elements, start=1):
        console.print(f"[{idx}] {element.get('text') or element.get('resource_id') or element.get('description') or 'Element'}")
        console.print(f"    type: {element.get('class_name', 'unknown')}")
        console.print(f"    text: {element.get('text')}")
        console.print(f"    resource_id: {element.get('resource_id')}")
        console.print(f"    clickable: {element.get('clickable')}")
        console.print(f"    bounds: {element.get('bounds')}")


@app.command("open")
def open_app(package: str) -> None:
    client = DroidPilotClient()
    result = client.open_app(package)
    console.print(f"[green]Opened app {package}[/green]")
    console.print(result)


@app.command("tap")
def tap(text: str | None = None, element: int | None = None) -> None:
    client = DroidPilotClient()
    result = client.tap(text=text, element_id=element)
    console.print("[green]Tapped target[/green]")
    console.print(result)


@app.command("type")
def type_text(value: str) -> None:
    client = DroidPilotClient()
    result = client.type_text(value)
    console.print(f"[green]Typed {value}[/green]")
    console.print(result)


@app.command("press")
def press(key: str) -> None:
    client = DroidPilotClient()
    result = client.press(key)
    console.print(f"[green]Pressed {key}[/green]")
    console.print(result)


@app.command("swipe")
def swipe(direction: str) -> None:
    client = DroidPilotClient()
    result = client.swipe(direction)
    console.print(f"[green]Swiped {direction}[/green]")
    console.print(result)


@app.command("scroll")
def scroll(direction: str) -> None:
    client = DroidPilotClient()
    result = client.scroll(direction)
    console.print(f"[green]Scrolled {direction}[/green]")
    console.print(result)


@app.command("history")
def history() -> None:
    client = DroidPilotClient()
    entries = client.history.list()
    if not entries:
        console.print("No history yet.")
        return
    for index, entry in enumerate(entries, start=1):
        action = entry.get("action", {})
        result = entry.get("result", {})
        console.print(f"[bold]Step {index}[/bold]")
        console.print(f"Action: {action.get('type')}")
        console.print(f"Data: {action}")
        console.print(f"Result: {result}")


@app.command("code")
def code() -> None:
    from .session.codegen import generate_python_code

    client = DroidPilotClient()
    code_str = generate_python_code(client.history)
    console.print(code_str)


@app.command("export")
def export_session(path: str) -> None:
    client = DroidPilotClient()
    saved_path = client.history.export(path)
    console.print(f"[green]Session exported to {saved_path}[/green]")


@app.command("run")
def run_goal(goal: str, max_steps: int = 20) -> None:
    client = DroidPilotClient()
    results = client.run_goal(goal, max_steps=max_steps)
    console.print(f"[green]Completed goal with {len(results)} steps[/green]")
    for result in results:
        console.print(result)


@app.command("shell")
def shell() -> None:
    console.print("[bold]DroidPilot[/bold]")
    console.print(
        "Type commands or natural-language goals like: "
        "'open Chrome and search for saketh' or 'open calculator'"
    )
    while True:
        try:
            cmd = input("DroidPilot > ")
        except EOFError:
            break
        stripped = cmd.strip()
        if not stripped:
            continue
        if stripped in {"exit", "quit"}:
            break

        try:
            normalized = normalize_shell_command(stripped)
            if normalized.startswith("run "):
                run_goal(normalized[4:].strip().strip('"').strip("'"))
                continue

            lowered = normalized.lower()
            if (
                lowered.startswith("go to ")
                or lowered.startswith("open ")
                or " and " in lowered
                or "type " in lowered
                or "search" in lowered
                or "calculator" in lowered
                or "settings" in lowered
            ):
                run_goal(normalized)
                continue

            parts = stripped.split()
            if parts[0] == "devices":
                devices()
            elif parts[0] == "connect":
                connect(parts[1] if len(parts) > 1 else None)
            elif parts[0] == "screenshot":
                screenshot(parts[1] if len(parts) > 1 else None)
            elif parts[0] == "inspect":
                inspect()
            elif parts[0] == "open":
                open_app(parts[1] if len(parts) > 1 else "")
            elif parts[0] == "tap":
                text = " ".join(parts[1:]) if len(parts) > 1 else None
                tap(text=text)
            elif parts[0] == "type":
                type_text(" ".join(parts[1:]))
            elif parts[0] == "press":
                press(parts[1] if len(parts) > 1 else "enter")
            elif parts[0] == "history":
                history()
            elif parts[0] == "code":
                code()
            else:
                # Treat unknown free-form text as a natural-language goal.
                run_goal(normalized)
        except Exception as exc:
            console.print(f"[red]Error:[/red] {exc}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
