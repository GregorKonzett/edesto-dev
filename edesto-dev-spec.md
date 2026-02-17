# edesto-dev: Use Claude Code for Embedded Development

## What This Is

`edesto-dev` is a tiny open-source CLI that does one thing: generate a CLAUDE.md file tailored to your board so Claude Code can autonomously write, flash, and validate firmware on real hardware.

The CLAUDE.md is the product. It teaches Claude Code the full development loop, including how to verify its own changes by reading serial output, making HTTP requests to the device, or checking sensor readings. Without this validation step, Claude Code can write and flash code but has no way of knowing if it actually worked.

**This is NOT another AI agent.** No accounts, no cloud, no extra subscription. You use Claude Code (which you already pay for). This just teaches it how to talk to your hardware.

## Installation

```
pipx install edesto-dev
```

The CLI command is `edesto`. It has one command that matters: `edesto init`.

## The Only Command: `edesto init`

```
edesto init                    # Interactive: detects board, asks questions
edesto init --board esp32      # Skip prompts, generate for ESP32
edesto init --board esp32s3
edesto init --board arduino-uno
```

**What it does:**
1. Detects connected boards via `arduino-cli board list --format json`
2. Detects the serial port (e.g. `/dev/ttyUSB0`, `/dev/cu.usbserial-*`)
3. Generates a `CLAUDE.md` in the current directory, pre-filled with:
   - Board FQBN and serial port
   - Compile, flash, and serial monitor commands
   - The full edit-compile-flash-validate workflow
   - Board-specific capabilities, pinout, and common pitfalls
   - Validation techniques (serial parsing, HTTP endpoints, GPIO checks)
4. Also generates a `.cursorrules` file with the same content for Cursor users.
5. If CLAUDE.md already exists, asks before overwriting.

**Also includes two utility commands:**
- `edesto doctor` -- checks arduino-cli, board core, serial port, permissions. Prints what's missing and how to fix it.
- `edesto boards` -- lists supported boards and detected devices.

## Tech Stack

- Python 3.10+
- `click` for CLI
- `pyserial` for serial port detection
- No other dependencies. No Jinja2, no colorama, nothing.

## Supported Boards

- `esp32` (FQBN: `esp32:esp32:esp32`)
- `esp32s3` (FQBN: `esp32:esp32:esp32s3`)
- `arduino-uno` (FQBN: `arduino:avr:uno`)
- `arduino-nano` (FQBN: `arduino:avr:nano`)
- `arduino-mega` (FQBN: `arduino:avr:mega`)

## The CLAUDE.md Template (This Is the Product)

The generated CLAUDE.md must teach Claude Code everything it needs to autonomously develop and validate firmware. The key sections are below. The template uses f-string placeholders like `{fqbn}`, `{port}`, `{board_name}` that get filled in by `edesto init`.

### Full CLAUDE.md template for ESP32:

```markdown
# Embedded Development: {board_name}

You are developing firmware for a {board_name} connected via USB.

## Hardware
- Board: {board_name}
- FQBN: {fqbn}
- Port: {port}
- Framework: Arduino
- Baud rate: 115200

## Commands

Compile:
arduino-cli compile --fqbn {fqbn} .

Flash:
arduino-cli upload --fqbn {fqbn} --port {port} .

## Development Loop

Every time you change code, follow this exact sequence:

1. Edit the .ino file (or .cpp/.h files)
2. Compile: `arduino-cli compile --fqbn {fqbn} .`
3. If compile fails, read the errors, fix them, and recompile. Do NOT flash broken code.
4. Flash: `arduino-cli upload --fqbn {fqbn} --port {port} .`
5. Wait 3 seconds for the board to reboot.
6. **Validate your changes** using one of the methods below.
7. If validation fails, go back to step 1 and iterate.

## Validation Methods

This is how you verify your code is actually working on the device. Always validate after flashing.

### Method 1: Read Serial Output

Use this Python snippet to capture serial output from the board:

```python
import serial, time
ser = serial.Serial('{port}', 115200, timeout=1)
time.sleep(3)  # Wait for boot
lines = []
start = time.time()
while time.time() - start < 10:  # Read for 10 seconds
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if line:
        lines.append(line)
        print(line)
ser.close()
```

Save this as `read_serial.py` and run with `python read_serial.py`. Parse the output to check if your firmware is behaving correctly.

**Important serial conventions for your firmware:**
- Always use `Serial.begin(115200)` in setup()
- Use `Serial.println()` (not `Serial.print()`) so each message is a complete line
- Print `[READY]` when initialization is complete
- Print `[ERROR] <description>` for any error conditions
- Use tags for structured output: `[SENSOR] temp=23.4`, `[WIFI] connected`, `[HTTP] server started on <ip>`

### Method 2: HTTP Requests (WiFi-enabled boards)

If the firmware runs a web server, you can validate by making HTTP requests:

```python
import serial, time, requests
# First, read serial to get the device's IP address
ser = serial.Serial('{port}', 115200, timeout=1)
time.sleep(5)
ip = None
start = time.time()
while time.time() - start < 15:
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if 'IP:' in line or 'ip:' in line:
        ip = line.split('IP:')[-1].strip() if 'IP:' in line else line.split('ip:')[-1].strip()
        break
ser.close()

if ip:
    response = requests.get(f'http://{ip}/health')
    print(f'Status: {response.status_code}')
    print(f'Body: {response.text}')
    print(f'Content-Type: {response.headers.get("Content-Type")}')
```

**Important:** When writing firmware with WiFi:
- Always print the IP address to serial on connection: `Serial.println("[WIFI] IP:" + WiFi.localIP().toString());`
- This lets the validation script find the device on the network.

### Method 3: GPIO/LED Visual Check

For simple projects, you can instruct the firmware to signal success/failure via the onboard LED:
- Pin 2 is the onboard LED on most ESP32 DevKit boards
- Blink pattern: 3 fast blinks = success, steady on = error
- This is a fallback when serial is not practical

## ESP32-Specific Information

### Capabilities
- WiFi 2.4GHz: `#include <WiFi.h>`
- Bluetooth: `#include <BluetoothSerial.h>`
- HTTP Server: `#include <WebServer.h>`
- OTA Updates: `#include <ArduinoOTA.h>`
- Persistent Storage: `#include <Preferences.h>`
- File System: `#include <SPIFFS.h>`

### Pin Reference
- GPIO 0: Boot button (do not use for general I/O)
- GPIO 2: Onboard LED
- GPIO 34-39: Input only (no pull-up/pull-down)
- I2C default: SDA=21, SCL=22
- SPI default: MOSI=23, MISO=19, SCK=18, SS=5
- ADC1: GPIO 32-39 (12-bit, works alongside WiFi)
- ADC2: GPIO 0,2,4,12-15,25-27 (does NOT work when WiFi is active)
- DAC: GPIO 25 (DAC1), GPIO 26 (DAC2)

### Common Pitfalls
- ADC2 pins do not work when WiFi is active. Use ADC1 pins (32-39) if you need analog reads with WiFi.
- WiFi and Bluetooth at full power simultaneously will cause instability. Use one at a time or reduce power.
- If upload fails with "connection timeout", hold the BOOT button while uploading.
- The ESP32 prints boot messages (`rst:`, `boot:`) on serial. Ignore these in your validation.
- `delay()` blocks the entire core. Use `millis()` for non-blocking timing.
- Stack size is 8KB per task by default. Use `xTaskCreate()` with a larger stack for complex tasks.
- OTA requires enough free flash for two firmware images. Use a partition scheme that supports this.
- `String` concatenation in loops causes heap fragmentation. Use `char[]` buffers for repeated operations.

### WiFi Connection Template
When writing WiFi code, use this pattern:
```cpp
#include <WiFi.h>
const char* ssid = "YOUR_SSID";        // User must fill in
const char* password = "YOUR_PASSWORD"; // User must fill in

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);
    Serial.print("[WIFI] Connecting");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    Serial.println("[WIFI] IP:" + WiFi.localIP().toString());
    Serial.println("[READY]");
}
```
```

**Board-specific templates:** Each board gets its own template with the right capabilities, pin references, and pitfalls. The ESP32 template above is the most detailed. Arduino boards get simpler versions without WiFi/BT sections.

## Example Projects

Three example projects in `examples/`. Each has an intentional bug for Claude Code to find and fix. These serve as demos and as the first-time onboarding experience.

### examples/sensor-debug/

A temperature sensor sketch with a unit conversion bug.

**sensor-debug.ino:**
- Simulates temperature readings (incrementing pattern based on `millis()`, no physical sensor needed)
- Converts Celsius to Fahrenheit
- Prints readings to serial: `[SENSOR] celsius=25.0 fahrenheit=77.0`
- **The bug:** Conversion uses `(celsius * 9/5) + 23` instead of `+ 32`

**CLAUDE.md:**
```markdown
# Sensor Debug Example

A temperature monitoring sketch that reads simulated sensor values and converts them.

## Expected Behavior
The sketch should print Celsius and Fahrenheit readings every 2 seconds.
The conversion formula is: F = (C * 9/5) + 32

## How to Validate
Run `python validate.py` after flashing. It reads serial output and checks that
the Fahrenheit values match the expected conversion from the Celsius values.

## Known Issue
Users report that Fahrenheit readings seem too low. The Celsius values look correct.
```

**validate.py:**
```python
import serial, time, sys

ser = serial.Serial('{port}', 115200, timeout=1)
time.sleep(3)

results = []
start = time.time()
while time.time() - start < 15 and len(results) < 5:
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if '[SENSOR]' in line:
        parts = dict(p.split('=') for p in line.split('[SENSOR]')[1].strip().split())
        c = float(parts['celsius'])
        f = float(parts['fahrenheit'])
        expected_f = (c * 9/5) + 32
        passed = abs(f - expected_f) < 0.1
        results.append(passed)
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] celsius={c} fahrenheit={f} expected={expected_f:.1f}")

ser.close()

if all(results) and len(results) >= 3:
    print("\nAll readings correct.")
    sys.exit(0)
else:
    print(f"\n{sum(results)}/{len(results)} readings correct.")
    sys.exit(1)
```

### examples/wifi-endpoint/

An ESP32 HTTP server with a Content-Type bug.

**wifi-endpoint.ino:**
- Connects to WiFi (credentials in `config.h`)
- Runs HTTP server on port 80
- GET /health returns `{"status": "ok", "uptime": <millis>}`
- **The bug:** Content-Type header is `text/plain` instead of `application/json`

**config.h.example:**
```cpp
#define WIFI_SSID "YOUR_SSID"
#define WIFI_PASSWORD "YOUR_PASSWORD"
```

**validate.py:**
- Reads serial to find the IP address (waits for `[WIFI] IP:` line)
- Makes GET request to /health
- Checks status code is 200
- Checks Content-Type is application/json
- Checks response body parses as valid JSON

### examples/ota-update/

An ESP32 with OTA support. Claude Code changes the version string and pushes an update over WiFi.

**ota-update.ino:**
- Connects to WiFi, enables ArduinoOTA
- Prints `[OTA] version=1.0.0` to serial and via HTTP GET /version
- OTA-capable so firmware can be updated wirelessly

**validate.py:**
- Reads current version from serial
- After OTA push, reads serial again to verify new version string

## Project Structure

```
edesto-dev/
├── README.md
├── LICENSE                    # MIT
├── pyproject.toml
├── edesto_dev/
│   ├── __init__.py           # Version string
│   ├── cli.py                # Click CLI: init, doctor, boards
│   ├── boards.py             # Board definitions and detection
│   └── templates/
│       ├── esp32.md
│       ├── esp32s3.md
│       ├── arduino_uno.md
│       ├── arduino_nano.md
│       └── arduino_mega.md
├── examples/
│   ├── sensor-debug/
│   │   ├── sensor-debug.ino
│   │   ├── CLAUDE.md
│   │   └── validate.py
│   ├── wifi-endpoint/
│   │   ├── wifi-endpoint.ino
│   │   ├── config.h.example
│   │   ├── CLAUDE.md
│   │   └── validate.py
│   └── ota-update/
│       ├── ota-update.ino
│       ├── CLAUDE.md
│       └── validate.py
└── tests/
    └── test_cli.py
```

## pyproject.toml

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "edesto-dev"
version = "0.1.0"
description = "Use Claude Code for embedded development. One command to set up the bridge between your AI agent and your hardware."
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
authors = [
    {name = "Edesto", email = "greg@edesto.com"},
]
keywords = ["embedded", "esp32", "arduino", "firmware", "ai", "claude", "development"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Embedded Systems",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]
dependencies = [
    "click>=8.0",
    "pyserial>=3.5",
]

[project.scripts]
edesto = "edesto_dev.cli:main"

[project.urls]
Homepage = "https://github.com/edesto/embedded-dev"
Repository = "https://github.com/edesto/embedded-dev"
```

## README.md Structure

1. **Hero GIF** -- Claude Code fixing a bug on a real ESP32. 30 seconds.
2. **One-liner** -- "You already have Claude Code. Here's how to use it for embedded development."
3. **Why** -- "AI coding agents stop at the terminal. `edesto init` teaches them how to compile, flash, and validate firmware on your actual hardware. No extra subscriptions. No cloud. No datasheets leaving your machine."
4. **Install + Quick Start:**
   ```
   pipx install edesto-dev
   edesto init --board esp32
   # Open Claude Code: "The sensor readings are wrong. Find and fix the bug."
   ```
5. **How it works** -- "edesto init generates a CLAUDE.md that gives your AI agent the full development loop: edit code, compile, flash to board, read serial output to verify it works, and iterate. The agent validates its own changes on real hardware."
6. **Examples** -- Three examples with brief descriptions
7. **Supported boards** -- Table
8. **About** -- "Built by Edesto. We build tools for robotics and embedded teams."

## Design Principles

1. The CLAUDE.md is the product. Everything else is scaffolding to generate it.
2. The validation section of the CLAUDE.md is the most important part. Without it, Claude Code is just deploying blind.
3. No accounts, no telemetry, no backend, no cloud.
4. Everything runs locally. Key differentiator from Embedder.
5. Keep the CLI minimal. One command that matters: `edesto init`.

## Build Order

1. Board definitions in `boards.py` (FQBN, capabilities, pin info, pitfalls per board)
2. CLAUDE.md templates with full validation instructions
3. `edesto init` with board detection and template generation
4. `edesto doctor` for environment checks
5. `edesto boards` for listing
6. `examples/sensor-debug/` with validate.py
7. `examples/wifi-endpoint/`
8. `examples/ota-update/`
9. README.md
10. pyproject.toml and packaging
