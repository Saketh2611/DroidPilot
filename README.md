# DroidPilot

DroidPilot is a Python CLI for AI-assisted Android automation. It listens to natural-language instructions from the shell or CLI, turns them into a structured action plan, validates each action, and executes it on a connected Android device over ADB and uiautomator2.

## What DroidPilot does

- Accepts user goals such as: `run "open Chrome and search for saketh"`
- Observes the current Android UI state
- Uses a planner agent (Gemini by default) to choose the next action
- Validates the action against a typed schema
- Executes the action on the phone
- Repeats until the goal is complete or a limit is reached

## Architecture: from user query to task execution

```mermaid
flowchart TD
    A[User query<br/>"open Chrome and search for saketh"] --> B[CLI / Shell]
    B --> C[Goal normalization]
    C --> D[Device state observation<br/>uiautomator2 + ADB]
    D --> E[Structured UI state<br/>DeviceState / UIElement]
    E --> F[Gemini planner<br/>google.genai]
    F --> G[Action schema<br/>tap / type / press / swipe / ...]
    G --> H[Validator]
    H --> I[Action executor]
    I --> J[Android device<br/>tap, type, press, launch, swipe]
    J --> K[Updated UI state]
    K --> F

    F -. fallback .-> L[Deterministic mock agent]
```

The execution loop is intentionally layered so the model never executes raw shell commands directly; it only produces structured actions that are validated before running on the device.

---

## Project layout

```text
DroidPilot/
├── src/
│   └── droidpilot/
│       ├── actions/
│       ├── agent/
│       ├── device/
│       ├── cli.py
│       ├── client.py
│       ├── config.py
│       ├── state/
│       └── __init__.py
├── tests/
├── .env.example
├── README.md
├── requirements.txt
├── pyproject.toml
├── LLM_DOC.txt
└── main.py
```

---

## Installation

1. Clone the repository:

```bash
git clone <repo-url>
cd DroidPilot
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -e ".[dev]"
```

---

## Install and configure ADB

ADB is required for communication between the PC and the Android device.

### Windows

1. Install Android Studio or Android SDK Platform Tools.
2. Add the `platform-tools` directory to your `PATH`.
3. Verify:

```bash
adb version
adb devices
```

### macOS

```bash
brew install android-platform-tools
```

### Linux

```bash
sudo apt update
sudo apt install android-tools-adb
```

---

## Android developer setup

1. On the Android device, enable Developer options.
2. Go to Settings > About phone.
3. Tap Build number 7 times.
4. Enable USB debugging under Settings > System > Developer options.
5. Connect the phone with USB and approve the debug prompt if shown.

Verify the device is visible:

```bash
adb devices
```

---

## Environment configuration

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-3.5-flash
DROIDPILOT_PROVIDER=gemini
DROIDPILOT_MAX_STEPS=20
DROIDPILOT_SCREENSHOT_DIR=./screenshots
```

The application reads these values through `pydantic-settings`.

---

## LLM setup

DroidPilot uses the supported Google GenAI SDK:

- `google.genai`
- not the deprecated `google.generativeai`

The model is expected to return a JSON action payload such as:

```json
{
  "type": "tap",
  "element_id": 153
}
```

or:

```json
{
  "type": "type",
  "text": "saketh"
}
```

The app also accepts compatibility variants like `{"action": "tap", ...}` before validation.

---

## Running DroidPilot

### List connected devices

```bash
droidpilot devices
```

### Connect to a device

```bash
droidpilot connect
```

### Basic commands

```bash
droidpilot screenshot
droidpilot inspect
droidpilot open chrome
droidpilot tap "Chrome"
droidpilot type "iQOO"
droidpilot press enter
droidpilot press home
droidpilot press back
droidpilot history
droidpilot code
```

### Interactive shell

```bash
droidpilot shell
```

Example shell inputs:

```text
DroidPilot > devices
DroidPilot > inspect
DroidPilot > tap "Chrome"
DroidPilot > type "iQOO"
DroidPilot > press enter
DroidPilot > screenshot
DroidPilot > run "open Chrome and search for saketh"
DroidPilot > go to Google and type saketh
```

If no API key is configured, the app falls back to the deterministic mock agent instead of failing.

---

## Execution flow in detail

1. The user enters a natural-language goal.
2. The CLI or shell forwards it into the client.
3. The agent observes the current Android state.
4. The planner emits a structured action.
5. The validator enforces the action schema.
6. The executor performs the actual UI operation.
7. The device state refreshes and the loop continues.

This pattern makes it easy to swap out the planner without changing the automation execution layer.

---

## Supported action types

- `tap`
- `type`
- `press`
- `launch_app`
- `swipe`
- `scroll`
- `home`
- `back`
- `wait`

---

## Safety boundary

The LLM does not execute raw shell commands. It only produces validated, typed actions such as `tap`, `type`, or `scroll`. Those actions are then executed via the Android adapter after validation.

---

## Troubleshooting

### Device not detected

```bash
adb devices
```

Make sure:
- USB debugging is enabled
- the device is trusted
- ADB is installed and on `PATH`

### UI element not found

- refresh the screen state
- inspect current hierarchy
- ensure the target element is visible and enabled

### LLM returns wrong schema

The app normalizes common output variants before validation. If the model still returns an invalid form, inspect the payload and adjust the prompt or tool contract.

---

## Additional docs

See [LLM_DOC.txt](LLM_DOC.txt) for the model contract and Gemini setup notes.

---

## Troubleshooting

### Device not detected

```bash
adb devices
```

Make sure:
- USB debugging is enabled
- the device is trusted
- ADB is installed and on `PATH`

### UI element not found

- refresh the screen state
- inspect current hierarchy
- ensure the target element is visible and enabled

### LLM returns wrong schema

The app normalizes common output variants before validation. If the model still returns an invalid form, inspect the payload and adjust the prompt or tool contract.

---

## Additional docs

See [LLM_DOC.txt](LLM_DOC.txt) for the model contract and Gemini setup notes.
