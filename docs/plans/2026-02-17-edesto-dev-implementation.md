# edesto-dev Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a CLI tool that generates CLAUDE.md files teaching Claude Code the full write → flash → validate loop for embedded hardware.

**Architecture:** Board definitions in `boards.py` provide all metadata (FQBN, capabilities, pins, pitfalls). A `templates.py` module assembles CLAUDE.md from board data using a common structure with board-specific sections. CLI uses Click. Serial-only validation in v1.

**Tech Stack:** Python 3.10+, click, pyserial, pytest

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `edesto_dev/__init__.py`
- Create: `edesto_dev/cli.py` (stub)
- Create: `edesto_dev/boards.py` (stub)
- Create: `edesto_dev/templates.py` (stub)
- Create: `tests/__init__.py`
- Create: `tests/test_boards.py` (stub)

**Step 1: Create pyproject.toml**

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

**Step 2: Create package files**

`edesto_dev/__init__.py`:
```python
__version__ = "0.1.0"
```

`edesto_dev/boards.py`:
```python
"""Board definitions for edesto-dev."""
```

`edesto_dev/templates.py`:
```python
"""CLAUDE.md template rendering for edesto-dev."""
```

`edesto_dev/cli.py`:
```python
"""CLI entry point for edesto-dev."""

import click


@click.group()
def main():
    """Use Claude Code for embedded development."""
    pass
```

`tests/__init__.py`: empty

`tests/test_boards.py`:
```python
"""Tests for board definitions."""
```

**Step 3: Create venv, install, and verify**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Note: Add `pytest` to dev dependencies in pyproject.toml:
```toml
[project.optional-dependencies]
dev = ["pytest>=7.0"]
```

Run: `python -m pytest tests/ -v`
Expected: 0 tests collected, no errors.

Run: `edesto --help`
Expected: Shows help with "Use Claude Code for embedded development."

**Step 4: Initialize git and commit**

```bash
git init
```

Create `.gitignore`:
```
__pycache__/
*.pyc
.venv/
*.egg-info/
dist/
build/
.DS_Store
```

```bash
git add .
git commit -m "chore: project scaffolding"
```

---

### Task 2: Board Data Model and ESP32 Board

**Files:**
- Modify: `edesto_dev/boards.py`
- Modify: `tests/test_boards.py`

**Step 1: Write failing tests for board data model**

`tests/test_boards.py`:
```python
"""Tests for board definitions."""

import pytest
from edesto_dev.boards import get_board, list_boards, BoardNotFoundError


class TestGetBoard:
    def test_esp32_returns_correct_fqbn(self):
        board = get_board("esp32")
        assert board.fqbn == "esp32:esp32:esp32"

    def test_esp32_has_name(self):
        board = get_board("esp32")
        assert board.name == "ESP32"

    def test_esp32_has_core(self):
        board = get_board("esp32")
        assert board.core == "esp32:esp32"

    def test_esp32_has_baud_rate(self):
        board = get_board("esp32")
        assert board.baud_rate == 115200

    def test_esp32_has_capabilities(self):
        board = get_board("esp32")
        assert "wifi" in board.capabilities
        assert "bluetooth" in board.capabilities

    def test_esp32_has_pins(self):
        board = get_board("esp32")
        assert "onboard_led" in board.pins
        assert board.pins["onboard_led"] == 2

    def test_esp32_has_pitfalls(self):
        board = get_board("esp32")
        assert len(board.pitfalls) > 0
        assert any("ADC2" in p for p in board.pitfalls)

    def test_unknown_board_raises(self):
        with pytest.raises(BoardNotFoundError):
            get_board("nonexistent")


class TestListBoards:
    def test_returns_list(self):
        boards = list_boards()
        assert isinstance(boards, list)
        assert len(boards) > 0

    def test_esp32_in_list(self):
        boards = list_boards()
        slugs = [b.slug for b in boards]
        assert "esp32" in slugs
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_boards.py -v`
Expected: FAIL with ImportError (BoardNotFoundError not defined)

**Step 3: Implement board data model and ESP32 definition**

`edesto_dev/boards.py`:
```python
"""Board definitions for edesto-dev."""

from dataclasses import dataclass, field


class BoardNotFoundError(Exception):
    """Raised when a board slug is not found."""
    pass


@dataclass
class Board:
    slug: str
    name: str
    fqbn: str
    core: str
    core_url: str
    baud_rate: int
    capabilities: list[str] = field(default_factory=list)
    pins: dict[str, int] = field(default_factory=dict)
    pitfalls: list[str] = field(default_factory=list)
    pin_notes: list[str] = field(default_factory=list)
    includes: dict[str, str] = field(default_factory=dict)


BOARDS: dict[str, Board] = {}


def _register(board: Board) -> Board:
    BOARDS[board.slug] = board
    return board


def get_board(slug: str) -> Board:
    """Get a board by its slug. Raises BoardNotFoundError if not found."""
    if slug not in BOARDS:
        raise BoardNotFoundError(f"Unknown board: {slug}. Use 'edesto boards' to list supported boards.")
    return BOARDS[slug]


def list_boards() -> list[Board]:
    """Return all supported boards."""
    return list(BOARDS.values())


# --- ESP32 Family ---

_register(Board(
    slug="esp32",
    name="ESP32",
    fqbn="esp32:esp32:esp32",
    core="esp32:esp32",
    core_url="https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json",
    baud_rate=115200,
    capabilities=["wifi", "bluetooth", "ble", "http_server", "ota", "spiffs", "preferences"],
    pins={
        "onboard_led": 2,
        "boot_button": 0,
        "i2c_sda": 21,
        "i2c_scl": 22,
        "spi_mosi": 23,
        "spi_miso": 19,
        "spi_sck": 18,
        "spi_ss": 5,
        "dac1": 25,
        "dac2": 26,
    },
    pin_notes=[
        "GPIO 0: Boot button — do not use for general I/O",
        "GPIO 2: Onboard LED",
        "GPIO 34-39: Input only (no pull-up/pull-down)",
        "ADC1: GPIO 32-39 (12-bit, works alongside WiFi)",
        "ADC2: GPIO 0,2,4,12-15,25-27 (does NOT work when WiFi is active)",
        "DAC: GPIO 25 (DAC1), GPIO 26 (DAC2)",
        "I2C default: SDA=21, SCL=22",
        "SPI default: MOSI=23, MISO=19, SCK=18, SS=5",
    ],
    pitfalls=[
        "ADC2 pins do not work when WiFi is active. Use ADC1 pins (32-39) if you need analog reads with WiFi.",
        "WiFi and Bluetooth at full power simultaneously will cause instability. Use one at a time or reduce power.",
        "If upload fails with 'connection timeout', hold the BOOT button while uploading.",
        "The ESP32 prints boot messages (rst:, boot:) on serial. Ignore these in your validation.",
        "delay() blocks the entire core. Use millis() for non-blocking timing.",
        "Stack size is 8KB per task by default. Use xTaskCreate() with a larger stack for complex tasks.",
        "OTA requires enough free flash for two firmware images. Use a partition scheme that supports this.",
        "String concatenation in loops causes heap fragmentation. Use char[] buffers for repeated operations.",
    ],
    includes={
        "wifi": "#include <WiFi.h>",
        "bluetooth": "#include <BluetoothSerial.h>",
        "http_server": "#include <WebServer.h>",
        "ota": "#include <ArduinoOTA.h>",
        "preferences": "#include <Preferences.h>",
        "spiffs": "#include <SPIFFS.h>",
    },
))
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_boards.py -v`
Expected: All 10 tests PASS

**Step 5: Commit**

```bash
git add edesto_dev/boards.py tests/test_boards.py
git commit -m "feat: board data model and ESP32 definition"
```

---

### Task 3: Remaining Board Definitions

**Files:**
- Modify: `edesto_dev/boards.py`
- Modify: `tests/test_boards.py`

**Step 1: Write failing tests for all boards**

Add to `tests/test_boards.py`:
```python
ALL_BOARD_SLUGS = [
    "esp32", "esp32s3", "esp32c3", "esp32c6",
    "esp8266",
    "arduino-uno", "arduino-nano", "arduino-mega",
    "rp2040",
    "teensy40", "teensy41",
    "stm32-nucleo",
]


class TestAllBoards:
    def test_all_boards_registered(self):
        boards = list_boards()
        slugs = [b.slug for b in boards]
        for expected in ALL_BOARD_SLUGS:
            assert expected in slugs, f"Missing board: {expected}"

    def test_total_board_count(self):
        assert len(list_boards()) == 12

    @pytest.mark.parametrize("slug", ALL_BOARD_SLUGS)
    def test_board_has_required_fields(self, slug):
        board = get_board(slug)
        assert board.name, f"{slug} missing name"
        assert board.fqbn, f"{slug} missing fqbn"
        assert board.core, f"{slug} missing core"
        assert board.baud_rate > 0, f"{slug} missing baud_rate"
        assert len(board.pitfalls) > 0, f"{slug} missing pitfalls"
        assert len(board.pin_notes) > 0, f"{slug} missing pin_notes"

    @pytest.mark.parametrize("slug", ["esp32", "esp32s3", "esp32c3", "esp32c6", "esp8266"])
    def test_wifi_boards_have_wifi_capability(self, slug):
        board = get_board(slug)
        assert "wifi" in board.capabilities

    @pytest.mark.parametrize("slug", ["arduino-uno", "arduino-nano", "arduino-mega", "rp2040"])
    def test_basic_boards_no_wifi(self, slug):
        board = get_board(slug)
        assert "wifi" not in board.capabilities

    @pytest.mark.parametrize("slug", ALL_BOARD_SLUGS)
    def test_board_fqbn_format(self, slug):
        board = get_board(slug)
        parts = board.fqbn.split(":")
        assert len(parts) == 3, f"{slug} FQBN should have 3 colon-separated parts"
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_boards.py -v`
Expected: FAIL — missing boards (only esp32 is registered)

**Step 3: Add all remaining board definitions**

Add to `edesto_dev/boards.py` after ESP32 definition:

```python
_register(Board(
    slug="esp32s3",
    name="ESP32-S3",
    fqbn="esp32:esp32:esp32s3",
    core="esp32:esp32",
    core_url="https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json",
    baud_rate=115200,
    capabilities=["wifi", "ble", "http_server", "ota", "spiffs", "preferences", "usb_native"],
    pins={
        "onboard_led": 48,
        "i2c_sda": 8,
        "i2c_scl": 9,
        "spi_mosi": 11,
        "spi_miso": 13,
        "spi_sck": 12,
        "spi_ss": 10,
    },
    pin_notes=[
        "GPIO 48: Onboard RGB LED (WS2812) on most DevKit boards",
        "GPIO 19/20: USB D-/D+ — do not use for general I/O if using native USB",
        "GPIO 0: Boot button / strapping pin",
        "ADC1: GPIO 1-10 (works alongside WiFi)",
        "ADC2: GPIO 11-20 (does NOT work when WiFi is active)",
        "I2C default: SDA=8, SCL=9",
        "SPI default: MOSI=11, MISO=13, SCK=12, SS=10",
    ],
    pitfalls=[
        "ADC2 pins do not work when WiFi is active. Use ADC1 pins if you need analog reads with WiFi.",
        "GPIO 19 and 20 are USB D-/D+. Do not use for general I/O if using native USB.",
        "The onboard LED on most S3 DevKit boards is an addressable RGB LED (WS2812) on GPIO 48, not a simple LED.",
        "If upload fails, hold BOOT button and press RST, then upload.",
        "delay() blocks the entire core. Use millis() for non-blocking timing.",
        "String concatenation in loops causes heap fragmentation. Use char[] buffers for repeated operations.",
    ],
    includes={
        "wifi": "#include <WiFi.h>",
        "http_server": "#include <WebServer.h>",
        "ota": "#include <ArduinoOTA.h>",
        "preferences": "#include <Preferences.h>",
        "spiffs": "#include <SPIFFS.h>",
    },
))

_register(Board(
    slug="esp32c3",
    name="ESP32-C3",
    fqbn="esp32:esp32:esp32c3",
    core="esp32:esp32",
    core_url="https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json",
    baud_rate=115200,
    capabilities=["wifi", "ble", "http_server", "ota", "spiffs", "preferences"],
    pins={
        "onboard_led": 8,
        "i2c_sda": 8,
        "i2c_scl": 9,
        "spi_mosi": 6,
        "spi_miso": 5,
        "spi_sck": 4,
        "spi_ss": 7,
    },
    pin_notes=[
        "GPIO 8: Onboard LED on most C3 DevKit boards",
        "GPIO 9: Boot button / strapping pin",
        "Only 22 GPIO pins available (GPIO 0-21)",
        "ADC1: GPIO 0-4 (works alongside WiFi)",
        "ADC2: not available on C3",
        "I2C default: SDA=8, SCL=9",
        "SPI default: MOSI=6, MISO=5, SCK=4, SS=7",
        "RISC-V single core — no dual-core task pinning",
    ],
    pitfalls=[
        "Single-core RISC-V — no xTaskCreatePinnedToCore(). Use xTaskCreate() instead.",
        "Only 22 GPIO pins. Plan pin usage carefully.",
        "GPIO 8 is both the onboard LED and default I2C SDA. Pick one use.",
        "If upload fails, hold BOOT (GPIO 9) and press RST, then upload.",
        "delay() blocks the only core. Use millis() for non-blocking timing.",
        "No Bluetooth Classic — only BLE is available.",
    ],
    includes={
        "wifi": "#include <WiFi.h>",
        "http_server": "#include <WebServer.h>",
        "ota": "#include <ArduinoOTA.h>",
        "preferences": "#include <Preferences.h>",
        "spiffs": "#include <SPIFFS.h>",
    },
))

_register(Board(
    slug="esp32c6",
    name="ESP32-C6",
    fqbn="esp32:esp32:esp32c6",
    core="esp32:esp32",
    core_url="https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json",
    baud_rate=115200,
    capabilities=["wifi", "wifi6", "ble", "zigbee", "thread", "http_server", "ota", "spiffs", "preferences"],
    pins={
        "onboard_led": 8,
        "i2c_sda": 6,
        "i2c_scl": 7,
        "spi_mosi": 19,
        "spi_miso": 20,
        "spi_sck": 21,
        "spi_ss": 18,
    },
    pin_notes=[
        "GPIO 8: Onboard LED on most C6 DevKit boards",
        "GPIO 9: Boot button / strapping pin",
        "30 GPIO pins available (GPIO 0-30)",
        "ADC1: GPIO 0-6 (works alongside WiFi)",
        "I2C default: SDA=6, SCL=7",
        "SPI default: MOSI=19, MISO=20, SCK=21, SS=18",
        "RISC-V single core (high-performance) + low-power core",
        "Supports IEEE 802.15.4 (Zigbee/Thread) on dedicated radio",
    ],
    pitfalls=[
        "Single high-performance RISC-V core — no dual-core task pinning.",
        "WiFi 6 support requires ESP-IDF v5.1+ (check your arduino-esp32 core version).",
        "Zigbee/Thread and WiFi share some radio resources. Throughput may be reduced when using both.",
        "If upload fails, hold BOOT (GPIO 9) and press RST, then upload.",
        "delay() blocks the main core. Use millis() for non-blocking timing.",
        "No Bluetooth Classic — only BLE is available.",
        "Arduino-esp32 core support for C6 is newer. Some libraries may not be fully compatible.",
    ],
    includes={
        "wifi": "#include <WiFi.h>",
        "http_server": "#include <WebServer.h>",
        "ota": "#include <ArduinoOTA.h>",
        "preferences": "#include <Preferences.h>",
        "spiffs": "#include <SPIFFS.h>",
    },
))

# --- ESP8266 ---

_register(Board(
    slug="esp8266",
    name="ESP8266",
    fqbn="esp8266:esp8266:nodemcuv2",
    core="esp8266:esp8266",
    core_url="https://arduino.esp8266.com/stable/package_esp8266com_index.json",
    baud_rate=115200,
    capabilities=["wifi", "http_server", "ota", "spiffs"],
    pins={
        "onboard_led": 2,
        "i2c_sda": 4,
        "i2c_scl": 5,
        "spi_mosi": 13,
        "spi_miso": 12,
        "spi_sck": 14,
        "spi_ss": 15,
    },
    pin_notes=[
        "GPIO 2: Onboard LED (active LOW on most NodeMCU boards)",
        "GPIO 0: Flash/Boot button — do not use for general I/O",
        "GPIO 16: Can be used for deep sleep wakeup (connect to RST)",
        "Only 1 ADC pin (A0), 10-bit resolution, 0-1V range",
        "I2C default: SDA=4 (D2), SCL=5 (D1)",
        "SPI default: MOSI=13 (D7), MISO=12 (D6), SCK=14 (D5), SS=15 (D8)",
        "NodeMCU D-pin labels differ from GPIO numbers. D1=GPIO5, D2=GPIO4, etc.",
    ],
    pitfalls=[
        "Only ~80KB usable RAM. Avoid large buffers and String concatenation.",
        "Single core — delay() blocks everything including WiFi stack. Use yield() or millis() patterns.",
        "GPIO 6-11 are connected to flash memory. Do NOT use them.",
        "The onboard LED is active LOW (digitalWrite(2, LOW) turns it ON).",
        "ADC reads 0-1V by default. NodeMCU has a voltage divider for 0-3.3V on A0.",
        "WDT (watchdog timer) will reset the board if you block for too long. Call yield() in long loops.",
        "Only supports 2.4GHz WiFi. No 5GHz.",
    ],
    includes={
        "wifi": "#include <ESP8266WiFi.h>",
        "http_server": "#include <ESP8266WebServer.h>",
        "ota": "#include <ArduinoOTA.h>",
        "spiffs": "#include <FS.h>",
    },
))

# --- Arduino AVR ---

_register(Board(
    slug="arduino-uno",
    name="Arduino Uno",
    fqbn="arduino:avr:uno",
    core="arduino:avr",
    core_url="",
    baud_rate=115200,
    capabilities=["digital_io", "analog_input", "pwm", "i2c", "spi", "uart"],
    pins={
        "onboard_led": 13,
        "i2c_sda": 18,
        "i2c_scl": 19,
        "spi_mosi": 11,
        "spi_miso": 12,
        "spi_sck": 13,
        "spi_ss": 10,
    },
    pin_notes=[
        "GPIO 13: Onboard LED (shared with SPI SCK)",
        "Analog pins A0-A5 (GPIO 14-19), 10-bit ADC",
        "PWM pins: 3, 5, 6, 9, 10, 11",
        "I2C: SDA=A4 (GPIO 18), SCL=A5 (GPIO 19)",
        "SPI: MOSI=11, MISO=12, SCK=13, SS=10",
        "Pin 13 LED will flicker during SPI communication",
        "Pins 0 and 1 are Serial RX/TX — avoid using for general I/O when using serial",
    ],
    pitfalls=[
        "Only 2KB SRAM and 32KB flash. Keep variables small and avoid String class.",
        "No hardware floating point. Float operations are slow and bloat code size.",
        "Pin 13 LED is also SPI SCK. It will blink during SPI transfers.",
        "Pins 0 (RX) and 1 (TX) are shared with USB serial. Don't connect peripherals to these.",
        "analogWrite() is PWM (0-255), not true analog output. No DAC on AVR.",
        "Interrupts only on pins 2 and 3 (INT0, INT1).",
        "delay() blocks everything. Use millis() for non-blocking timing.",
        "No WiFi or Bluetooth. Communication is serial only.",
    ],
    includes={},
))

_register(Board(
    slug="arduino-nano",
    name="Arduino Nano",
    fqbn="arduino:avr:nano",
    core="arduino:avr",
    core_url="",
    baud_rate=115200,
    capabilities=["digital_io", "analog_input", "pwm", "i2c", "spi", "uart"],
    pins={
        "onboard_led": 13,
        "i2c_sda": 18,
        "i2c_scl": 19,
        "spi_mosi": 11,
        "spi_miso": 12,
        "spi_sck": 13,
        "spi_ss": 10,
    },
    pin_notes=[
        "GPIO 13: Onboard LED (shared with SPI SCK)",
        "Analog pins A0-A7 (A6 and A7 are analog input ONLY, no digital)",
        "PWM pins: 3, 5, 6, 9, 10, 11",
        "I2C: SDA=A4 (GPIO 18), SCL=A5 (GPIO 19)",
        "SPI: MOSI=11, MISO=12, SCK=13, SS=10",
        "Pins 0 and 1 are Serial RX/TX",
    ],
    pitfalls=[
        "Only 2KB SRAM and 32KB flash. Keep variables small and avoid String class.",
        "A6 and A7 are analog input ONLY — they cannot be used as digital pins.",
        "Some Nano clones use the old bootloader. If upload fails, select 'ATmega328P (Old Bootloader)' in board settings or use --fqbn arduino:avr:nano:cpu=atmega328old.",
        "No hardware floating point. Float operations are slow.",
        "Pins 0 (RX) and 1 (TX) are shared with USB serial.",
        "Interrupts only on pins 2 and 3.",
        "delay() blocks everything. Use millis() for non-blocking timing.",
        "No WiFi or Bluetooth. Communication is serial only.",
    ],
    includes={},
))

_register(Board(
    slug="arduino-mega",
    name="Arduino Mega 2560",
    fqbn="arduino:avr:mega",
    core="arduino:avr",
    core_url="",
    baud_rate=115200,
    capabilities=["digital_io", "analog_input", "pwm", "i2c", "spi", "uart", "multi_serial"],
    pins={
        "onboard_led": 13,
        "i2c_sda": 20,
        "i2c_scl": 21,
        "spi_mosi": 51,
        "spi_miso": 50,
        "spi_sck": 52,
        "spi_ss": 53,
    },
    pin_notes=[
        "GPIO 13: Onboard LED",
        "Analog pins A0-A15 (16 analog inputs), 10-bit ADC",
        "PWM pins: 2-13, 44-46",
        "I2C: SDA=20, SCL=21",
        "SPI: MOSI=51, MISO=50, SCK=52, SS=53",
        "4 hardware serial ports: Serial (0/1), Serial1 (18/19), Serial2 (16/17), Serial3 (14/15)",
        "External interrupts on pins 2, 3, 18, 19, 20, 21",
    ],
    pitfalls=[
        "8KB SRAM and 256KB flash — more than Uno/Nano but still limited.",
        "No hardware floating point. Float operations are slow.",
        "SPI pins are on 50-53, NOT 11-13 like Uno/Nano. Shields designed for Uno may not work.",
        "Pin 53 (SS) must be kept as OUTPUT for SPI master mode, even if not used as SS.",
        "analogWrite() is PWM, not true analog. No DAC on AVR.",
        "delay() blocks everything. Use millis() for non-blocking timing.",
        "No WiFi or Bluetooth. Communication is serial only.",
    ],
    includes={},
))

# --- RP2040 ---

_register(Board(
    slug="rp2040",
    name="Raspberry Pi Pico (RP2040)",
    fqbn="rp2040:rp2040:rpipico",
    core="rp2040:rp2040",
    core_url="https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json",
    baud_rate=115200,
    capabilities=["digital_io", "analog_input", "pwm", "i2c", "spi", "uart", "pio", "dual_core", "usb_native"],
    pins={
        "onboard_led": 25,
        "i2c_sda": 4,
        "i2c_scl": 5,
        "spi_mosi": 19,
        "spi_miso": 16,
        "spi_sck": 18,
        "spi_ss": 17,
    },
    pin_notes=[
        "GPIO 25: Onboard LED",
        "ADC: GPIO 26-28 (3 channels, 12-bit), GPIO 29 reads VSYS/3",
        "PWM: All GPIO pins support PWM (16 PWM channels, 8 slices)",
        "I2C0: SDA=4, SCL=5 (can be remapped to other pins)",
        "I2C1: SDA=6, SCL=7",
        "SPI0: MOSI=19, MISO=16, SCK=18, SS=17",
        "SPI1: MOSI=15, MISO=12, SCK=14, SS=13",
        "UART0: TX=0, RX=1",
        "UART1: TX=8, RX=9",
        "PIO: 2 PIO blocks with 4 state machines each — can emulate almost any protocol",
    ],
    pitfalls=[
        "264KB SRAM, 2MB flash. More than AVR but still watch memory usage.",
        "For first-time upload: hold BOOTSEL button while plugging in USB. After that, serial upload works normally.",
        "GPIO 25 is the onboard LED on Pico. On Pico W, the LED is on the WiFi chip (use LED_BUILTIN).",
        "ADC has a known offset error. Calibrate for precision measurements.",
        "USB serial (Serial) and hardware UART (Serial1, Serial2) are separate. Serial is USB CDC.",
        "No EEPROM — use LittleFS or flash storage for persistent data.",
        "delay() only blocks the current core. The other core keeps running.",
        "Dual core: use setup1()/loop1() for the second core in Arduino framework.",
    ],
    includes={},
))

# --- Teensy ---

_register(Board(
    slug="teensy40",
    name="Teensy 4.0",
    fqbn="teensy:avr:teensy40",
    core="teensy:avr",
    core_url="https://www.pjrc.com/teensy/package_teensy_index.json",
    baud_rate=115200,
    capabilities=["digital_io", "analog_input", "pwm", "i2c", "spi", "uart", "usb_native", "audio", "can_bus"],
    pins={
        "onboard_led": 13,
        "i2c_sda": 18,
        "i2c_scl": 19,
        "spi_mosi": 11,
        "spi_miso": 12,
        "spi_sck": 13,
        "spi_ss": 10,
    },
    pin_notes=[
        "GPIO 13: Onboard LED",
        "ADC: 14 analog input pins, 12-bit resolution (configurable to 10/12/16-bit)",
        "PWM: Pins 0-9, 22, 23, 24, 25, 28, 29, 33, 36, 37",
        "I2C: 3 buses — I2C0 (18/19), I2C1 (16/17), I2C2 (24/25)",
        "SPI: 2 buses — SPI0 (11/12/13), SPI1 (26/1/27)",
        "UART: 7 hardware serial ports (Serial1 through Serial7)",
        "CAN bus: CAN1 (22/23), CAN2 (0/1)",
        "USB is native — Serial is always available at any baud rate",
    ],
    pitfalls=[
        "Teensy uses its own upload tool (teensy_loader_cli), not standard serial upload. Install Teensyduino.",
        "USB serial (Serial) is native USB CDC — baud rate setting is ignored but Serial.begin() is still required.",
        "600MHz ARM Cortex-M7 — extremely fast but runs hot under full load.",
        "1024KB flash, 512KB RAM (TCM) + 512KB RAM2 (OCRAM). Use EXTMEM for PSRAM if available.",
        "No WiFi or Bluetooth built in. Use external modules or Teensy 4.1 with Ethernet.",
        "The Teensy bootloader activates with a physical button press. No serial DTR reset like Arduino.",
        "analogReadResolution() can be set to 10, 12, or 16 bits. Default is 10 for Arduino compatibility.",
        "delay() blocks but elapsedMillis/elapsedMicros classes provide non-blocking alternatives.",
    ],
    includes={},
))

_register(Board(
    slug="teensy41",
    name="Teensy 4.1",
    fqbn="teensy:avr:teensy41",
    core="teensy:avr",
    core_url="https://www.pjrc.com/teensy/package_teensy_index.json",
    baud_rate=115200,
    capabilities=["digital_io", "analog_input", "pwm", "i2c", "spi", "uart", "usb_native", "audio", "can_bus", "ethernet", "sd_card"],
    pins={
        "onboard_led": 13,
        "i2c_sda": 18,
        "i2c_scl": 19,
        "spi_mosi": 11,
        "spi_miso": 12,
        "spi_sck": 13,
        "spi_ss": 10,
    },
    pin_notes=[
        "GPIO 13: Onboard LED",
        "ADC: 18 analog input pins, 12-bit resolution (configurable to 10/12/16-bit)",
        "PWM: Pins 0-9, 22, 23, 24, 25, 28, 29, 33, 36, 37",
        "I2C: 3 buses — I2C0 (18/19), I2C1 (16/17), I2C2 (24/25)",
        "SPI: 2 buses — SPI0 (11/12/13), SPI1 (26/39/27)",
        "UART: 8 hardware serial ports (Serial1 through Serial8)",
        "Ethernet: Native 10/100 Mbit (requires MagJack or connector on bottom pads)",
        "SD card: Built-in SDIO slot on bottom of board",
        "USB Host: 5-pin header for USB host mode",
        "PSRAM: Optional 8MB/16MB PSRAM via bottom pads",
    ],
    pitfalls=[
        "Teensy uses its own upload tool (teensy_loader_cli). Install Teensyduino.",
        "USB serial (Serial) is native USB CDC — baud rate setting is ignored.",
        "Ethernet requires a MagJack soldered to the bottom pads. It is NOT plug-and-play.",
        "SD card slot is on the bottom of the board. Use SD.begin(BUILTIN_SDCARD).",
        "PSRAM (if soldered) is accessed via EXTMEM keyword. Not all memory allocations use it automatically.",
        "8MB flash, 512KB RAM (TCM) + 512KB RAM2 + optional PSRAM.",
        "The Teensy bootloader activates with a physical button press. No serial DTR reset.",
        "delay() blocks but elapsedMillis/elapsedMicros classes provide non-blocking alternatives.",
    ],
    includes={},
))

# --- STM32 ---

_register(Board(
    slug="stm32-nucleo",
    name="STM32 Nucleo-64",
    fqbn="STMicroelectronics:stm32:Nucleo_64",
    core="STMicroelectronics:stm32",
    core_url="https://github.com/stm32duino/BoardManagerFiles/raw/main/package_stmicroelectronics_index.json",
    baud_rate=115200,
    capabilities=["digital_io", "analog_input", "pwm", "i2c", "spi", "uart", "dac", "can_bus"],
    pins={
        "onboard_led": 13,
        "i2c_sda": 14,
        "i2c_scl": 15,
        "spi_mosi": 11,
        "spi_miso": 12,
        "spi_sck": 13,
        "spi_ss": 10,
    },
    pin_notes=[
        "LED: LD2 (green) on PA5 / D13 (Arduino-compatible header)",
        "User button: B1 on PC13",
        "Arduino-compatible pin headers: D0-D15, A0-A5",
        "ADC: A0-A5, 12-bit resolution",
        "DAC: Available on some Nucleo variants (check your specific board)",
        "I2C: SDA=D14, SCL=D15 (Arduino header mapping)",
        "SPI: MOSI=D11, MISO=D12, SCK=D13, SS=D10",
        "UART: Multiple USARTs available. Serial uses ST-Link VCP (Virtual COM Port).",
    ],
    pitfalls=[
        "The Nucleo-64 family includes many different STM32 chips. Verify your specific variant.",
        "Upload uses ST-Link debugger built into the Nucleo board. No USB serial upload.",
        "Serial output goes through the ST-Link Virtual COM Port, not a direct USB connection.",
        "The Arduino pin mapping (D0, D1, etc.) differs from the STM32 native pin names (PA0, PB3, etc.).",
        "Some STM32duino libraries differ from standard Arduino libraries. Check compatibility.",
        "Flash and RAM size vary by STM32 variant. Check your specific chip's datasheet.",
        "If upload fails, ensure ST-Link drivers are installed and the board is detected.",
        "delay() blocks everything. Use millis() or HAL_GetTick() for non-blocking timing.",
    ],
    includes={},
))
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_boards.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add edesto_dev/boards.py tests/test_boards.py
git commit -m "feat: add all 12 board definitions"
```

---

### Task 4: Template Rendering — Core Structure

**Files:**
- Modify: `edesto_dev/templates.py`
- Create: `tests/test_templates.py`

**Step 1: Write failing tests for template rendering**

`tests/test_templates.py`:
```python
"""Tests for CLAUDE.md template rendering."""

import pytest
from edesto_dev.boards import get_board, list_boards
from edesto_dev.templates import render_template


class TestRenderTemplate:
    def test_contains_board_name(self):
        board = get_board("esp32")
        result = render_template(board, port="/dev/ttyUSB0")
        assert "ESP32" in result

    def test_contains_fqbn(self):
        board = get_board("esp32")
        result = render_template(board, port="/dev/ttyUSB0")
        assert "esp32:esp32:esp32" in result

    def test_contains_port(self):
        board = get_board("esp32")
        result = render_template(board, port="/dev/ttyUSB0")
        assert "/dev/ttyUSB0" in result

    def test_no_unfilled_placeholders(self):
        board = get_board("esp32")
        result = render_template(board, port="/dev/ttyUSB0")
        # Check no {placeholder} patterns remain
        import re
        placeholders = re.findall(r"\{[a-z_]+\}", result)
        assert placeholders == [], f"Unfilled placeholders: {placeholders}"

    def test_has_hardware_section(self):
        board = get_board("esp32")
        result = render_template(board, port="/dev/ttyUSB0")
        assert "## Hardware" in result

    def test_has_commands_section(self):
        board = get_board("esp32")
        result = render_template(board, port="/dev/ttyUSB0")
        assert "## Commands" in result
        assert "arduino-cli compile" in result
        assert "arduino-cli upload" in result

    def test_has_development_loop(self):
        board = get_board("esp32")
        result = render_template(board, port="/dev/ttyUSB0")
        assert "## Development Loop" in result
        assert "Compile" in result
        assert "Flash" in result
        assert "Validate" in result

    def test_has_serial_validation(self):
        board = get_board("esp32")
        result = render_template(board, port="/dev/ttyUSB0")
        assert "serial.Serial" in result
        assert "[READY]" in result
        assert "115200" in result

    def test_has_serial_conventions(self):
        board = get_board("esp32")
        result = render_template(board, port="/dev/ttyUSB0")
        assert "Serial.begin(115200)" in result
        assert "[READY]" in result
        assert "[ERROR]" in result
        assert "[SENSOR]" in result

    def test_has_board_specific_section(self):
        board = get_board("esp32")
        result = render_template(board, port="/dev/ttyUSB0")
        assert "Pin Reference" in result
        assert "Common Pitfalls" in result

    def test_has_pitfalls(self):
        board = get_board("esp32")
        result = render_template(board, port="/dev/ttyUSB0")
        assert "ADC2" in result

    def test_has_pin_notes(self):
        board = get_board("esp32")
        result = render_template(board, port="/dev/ttyUSB0")
        assert "GPIO 2: Onboard LED" in result

    def test_wifi_board_has_capabilities(self):
        board = get_board("esp32")
        result = render_template(board, port="/dev/ttyUSB0")
        assert "Capabilities" in result
        assert "#include <WiFi.h>" in result

    def test_non_wifi_board_no_wifi_includes(self):
        board = get_board("arduino-uno")
        result = render_template(board, port="/dev/ttyUSB0")
        assert "WiFi.h" not in result


class TestAllBoardsRender:
    @pytest.mark.parametrize("slug", [b.slug for b in list_boards()])
    def test_renders_without_error(self, slug):
        board = get_board(slug)
        result = render_template(board, port="/dev/ttyUSB0")
        assert len(result) > 100

    @pytest.mark.parametrize("slug", [b.slug for b in list_boards()])
    def test_contains_fqbn(self, slug):
        board = get_board(slug)
        result = render_template(board, port="/dev/ttyUSB0")
        assert board.fqbn in result

    @pytest.mark.parametrize("slug", [b.slug for b in list_boards()])
    def test_has_validation_section(self, slug):
        board = get_board(slug)
        result = render_template(board, port="/dev/ttyUSB0")
        assert "Validation" in result
        assert "serial.Serial" in result

    @pytest.mark.parametrize("slug", [b.slug for b in list_boards()])
    def test_has_development_loop(self, slug):
        board = get_board(slug)
        result = render_template(board, port="/dev/ttyUSB0")
        assert "Development Loop" in result

    @pytest.mark.parametrize("slug", [b.slug for b in list_boards()])
    def test_no_unfilled_placeholders(self, slug):
        board = get_board(slug)
        result = render_template(board, port="/dev/ttyUSB0")
        import re
        placeholders = re.findall(r"\{[a-z_]+\}", result)
        assert placeholders == [], f"Unfilled placeholders in {slug}: {placeholders}"
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_templates.py -v`
Expected: FAIL with ImportError (render_template not defined)

**Step 3: Implement render_template**

`edesto_dev/templates.py`:
```python
"""CLAUDE.md template rendering for edesto-dev."""

from edesto_dev.boards import Board


def render_template(board: Board, port: str) -> str:
    """Render a complete CLAUDE.md for the given board and port."""
    sections = [
        _header(board, port),
        _commands(board, port),
        _dev_loop(board, port),
        _validation(board, port),
        _board_info(board),
    ]
    return "\n".join(sections)


def _header(board: Board, port: str) -> str:
    return f"""# Embedded Development: {board.name}

You are developing firmware for a {board.name} connected via USB.

## Hardware
- Board: {board.name}
- FQBN: {board.fqbn}
- Port: {port}
- Framework: Arduino
- Baud rate: {board.baud_rate}"""


def _commands(board: Board, port: str) -> str:
    return f"""
## Commands

Compile:
```
arduino-cli compile --fqbn {board.fqbn} .
```

Flash:
```
arduino-cli upload --fqbn {board.fqbn} --port {port} .
```"""


def _dev_loop(board: Board, port: str) -> str:
    return f"""
## Development Loop

Every time you change code, follow this exact sequence:

1. Edit the .ino file (or .cpp/.h files)
2. Compile: `arduino-cli compile --fqbn {board.fqbn} .`
3. If compile fails, read the errors, fix them, and recompile. Do NOT flash broken code.
4. Flash: `arduino-cli upload --fqbn {board.fqbn} --port {port} .`
5. Wait 3 seconds for the board to reboot.
6. **Validate your changes** using the method below.
7. If validation fails, go back to step 1 and iterate."""


def _validation(board: Board, port: str) -> str:
    return f"""
## Validation

This is how you verify your code is actually working on the device. Always validate after flashing.

### Read Serial Output

Use this Python snippet to capture serial output from the board:

```python
import serial, time
ser = serial.Serial('{port}', {board.baud_rate}, timeout=1)
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
- Always use `Serial.begin({board.baud_rate})` in setup()
- Use `Serial.println()` (not `Serial.print()`) so each message is a complete line
- Print `[READY]` when initialization is complete
- Print `[ERROR] <description>` for any error conditions
- Use tags for structured output: `[SENSOR] temp=23.4`, `[STATUS] running`"""


def _board_info(board: Board) -> str:
    parts = [f"\n## {board.name}-Specific Information"]

    # Capabilities with includes
    if board.includes:
        parts.append("\n### Capabilities")
        for cap, include in board.includes.items():
            parts.append(f"- {cap.replace('_', ' ').title()}: `{include}`")

    # Pin reference
    if board.pin_notes:
        parts.append("\n### Pin Reference")
        for note in board.pin_notes:
            parts.append(f"- {note}")

    # Pitfalls
    if board.pitfalls:
        parts.append("\n### Common Pitfalls")
        for pitfall in board.pitfalls:
            parts.append(f"- {pitfall}")

    return "\n".join(parts)
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_templates.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add edesto_dev/templates.py tests/test_templates.py
git commit -m "feat: CLAUDE.md template rendering with serial validation"
```

---

### Task 5: CLI — `edesto init` Command

**Files:**
- Modify: `edesto_dev/cli.py`
- Create: `tests/test_cli.py`

**Step 1: Write failing tests for init command**

`tests/test_cli.py`:
```python
"""Tests for the edesto CLI."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from edesto_dev.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestInit:
    def test_init_with_board_and_port(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "--board", "esp32", "--port", "/dev/ttyUSB0"])
            assert result.exit_code == 0
            assert Path("CLAUDE.md").exists()

    def test_init_generates_valid_content(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "--board", "esp32", "--port", "/dev/ttyUSB0"])
            content = Path("CLAUDE.md").read_text()
            assert "esp32:esp32:esp32" in content
            assert "/dev/ttyUSB0" in content
            assert "Development Loop" in content

    def test_init_also_creates_cursorrules(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "--board", "esp32", "--port", "/dev/ttyUSB0"])
            assert Path(".cursorrules").exists()
            # Same content as CLAUDE.md
            claude = Path("CLAUDE.md").read_text()
            cursor = Path(".cursorrules").read_text()
            assert claude == cursor

    def test_init_unknown_board_fails(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "--board", "nonexistent", "--port", "/dev/ttyUSB0"])
            assert result.exit_code != 0
            assert "Unknown board" in result.output

    def test_init_asks_before_overwrite(self, runner):
        with runner.isolated_filesystem():
            Path("CLAUDE.md").write_text("existing content")
            result = runner.invoke(main, ["init", "--board", "esp32", "--port", "/dev/ttyUSB0"], input="n\n")
            assert result.exit_code == 0
            assert Path("CLAUDE.md").read_text() == "existing content"

    def test_init_overwrites_when_confirmed(self, runner):
        with runner.isolated_filesystem():
            Path("CLAUDE.md").write_text("existing content")
            result = runner.invoke(main, ["init", "--board", "esp32", "--port", "/dev/ttyUSB0"], input="y\n")
            assert result.exit_code == 0
            assert "esp32:esp32:esp32" in Path("CLAUDE.md").read_text()

    def test_init_all_boards_work(self, runner):
        from edesto_dev.boards import list_boards
        for board in list_boards():
            with runner.isolated_filesystem():
                result = runner.invoke(main, ["init", "--board", board.slug, "--port", "/dev/ttyUSB0"])
                assert result.exit_code == 0, f"Failed for {board.slug}: {result.output}"
                assert Path("CLAUDE.md").exists()
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_cli.py -v`
Expected: FAIL (init command not defined)

**Step 3: Implement init command**

`edesto_dev/cli.py`:
```python
"""CLI entry point for edesto-dev."""

from pathlib import Path

import click

from edesto_dev.boards import get_board, list_boards, BoardNotFoundError
from edesto_dev.templates import render_template


@click.group()
def main():
    """Use Claude Code for embedded development."""
    pass


@main.command()
@click.option("--board", type=str, help="Board slug (e.g. esp32, arduino-uno). Use 'edesto boards' to list.")
@click.option("--port", type=str, help="Serial port (e.g. /dev/ttyUSB0, /dev/cu.usbserial-0001).")
def init(board, port):
    """Generate a CLAUDE.md for your board."""
    if not board:
        click.echo("Error: --board is required. Use 'edesto boards' to list supported boards.")
        raise SystemExit(1)

    if not port:
        click.echo("Error: --port is required. Check 'ls /dev/tty*' or 'ls /dev/cu.*' for your serial port.")
        raise SystemExit(1)

    try:
        board_def = get_board(board)
    except BoardNotFoundError as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)

    content = render_template(board_def, port=port)

    claude_path = Path("CLAUDE.md")
    cursor_path = Path(".cursorrules")

    if claude_path.exists():
        if not click.confirm("CLAUDE.md already exists. Overwrite?"):
            click.echo("Aborted.")
            return

    claude_path.write_text(content)
    cursor_path.write_text(content)

    click.echo(f"Generated CLAUDE.md for {board_def.name} on {port}")
    click.echo(f"Also created .cursorrules for Cursor users.")
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_cli.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add edesto_dev/cli.py tests/test_cli.py
git commit -m "feat: edesto init command"
```

---

### Task 6: CLI — `edesto boards` Command

**Files:**
- Modify: `edesto_dev/cli.py`
- Modify: `tests/test_cli.py`

**Step 1: Write failing tests**

Add to `tests/test_cli.py`:
```python
class TestBoards:
    def test_boards_lists_all(self, runner):
        result = runner.invoke(main, ["boards"])
        assert result.exit_code == 0
        assert "esp32" in result.output
        assert "arduino-uno" in result.output
        assert "rp2040" in result.output

    def test_boards_shows_fqbn(self, runner):
        result = runner.invoke(main, ["boards"])
        assert "esp32:esp32:esp32" in result.output

    def test_boards_shows_all_board_count(self, runner):
        from edesto_dev.boards import list_boards
        result = runner.invoke(main, ["boards"])
        for board in list_boards():
            assert board.slug in result.output, f"Missing {board.slug} in output"
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_cli.py::TestBoards -v`
Expected: FAIL

**Step 3: Implement boards command**

Add to `edesto_dev/cli.py`:
```python
@main.command()
def boards():
    """List supported boards."""
    board_list = list_boards()
    click.echo(f"Supported boards ({len(board_list)}):\n")
    click.echo(f"  {'Slug':<20} {'Name':<30} {'FQBN'}")
    click.echo(f"  {'─' * 20} {'─' * 30} {'─' * 40}")
    for b in board_list:
        click.echo(f"  {b.slug:<20} {b.name:<30} {b.fqbn}")
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_cli.py::TestBoards -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add edesto_dev/cli.py tests/test_cli.py
git commit -m "feat: edesto boards command"
```

---

### Task 7: CLI — `edesto doctor` Command

**Files:**
- Modify: `edesto_dev/cli.py`
- Modify: `tests/test_cli.py`

**Step 1: Write failing tests**

Add to `tests/test_cli.py`:
```python
class TestDoctor:
    def test_doctor_runs(self, runner):
        result = runner.invoke(main, ["doctor"])
        assert result.exit_code == 0

    def test_doctor_checks_arduino_cli(self, runner):
        result = runner.invoke(main, ["doctor"])
        assert "arduino-cli" in result.output

    @patch("shutil.which", return_value=None)
    def test_doctor_warns_missing_arduino_cli(self, mock_which, runner):
        result = runner.invoke(main, ["doctor"])
        assert "not found" in result.output.lower() or "missing" in result.output.lower() or "not installed" in result.output.lower()
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_cli.py::TestDoctor -v`
Expected: FAIL

**Step 3: Implement doctor command**

Add to `edesto_dev/cli.py` (add `import shutil, subprocess, glob as globmod` at top):
```python
import glob as globmod
import shutil
import subprocess


@main.command()
def doctor():
    """Check your environment for embedded development."""
    ok = True

    # Check arduino-cli
    arduino_cli = shutil.which("arduino-cli")
    if arduino_cli:
        click.echo(f"[OK] arduino-cli found: {arduino_cli}")
        # Check version
        try:
            version = subprocess.run(
                ["arduino-cli", "version"],
                capture_output=True, text=True, timeout=5
            )
            click.echo(f"     {version.stdout.strip()}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    else:
        click.echo("[!!] arduino-cli not found. Install: https://arduino.github.io/arduino-cli/installation/")
        ok = False

    # Check serial ports
    ports = globmod.glob("/dev/ttyUSB*") + globmod.glob("/dev/ttyACM*") + globmod.glob("/dev/cu.usb*")
    if ports:
        click.echo(f"[OK] Serial ports found:")
        for p in ports:
            click.echo(f"     {p}")
    else:
        click.echo("[!!] No serial ports detected. Is a board connected via USB?")
        ok = False

    # Check Python serial
    try:
        import serial
        click.echo(f"[OK] pyserial installed: {serial.__version__}")
    except ImportError:
        click.echo("[!!] pyserial not installed. Run: pip install pyserial")
        ok = False

    if ok:
        click.echo("\nAll checks passed. Ready for embedded development.")
    else:
        click.echo("\nSome checks failed. Fix the issues above before running 'edesto init'.")
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_cli.py::TestDoctor -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add edesto_dev/cli.py tests/test_cli.py
git commit -m "feat: edesto doctor command"
```

---

### Task 8: Examples — sensor-debug

**Files:**
- Create: `examples/sensor-debug/sensor-debug.ino`
- Create: `examples/sensor-debug/CLAUDE.md`
- Create: `examples/sensor-debug/validate.py`

**Step 1: Create sensor-debug example**

`examples/sensor-debug/sensor-debug.ino`:
```cpp
// Temperature sensor simulation with conversion bug
// The Fahrenheit conversion has an intentional error for Claude Code to find

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("[READY]");
}

void loop() {
    // Simulate temperature reading (incrementing pattern)
    float celsius = 20.0 + (millis() / 10000.0);
    if (celsius > 40.0) celsius = 20.0 + fmod(celsius - 20.0, 20.0);

    // BUG: Should be + 32, not + 23
    float fahrenheit = (celsius * 9.0 / 5.0) + 23;

    Serial.print("[SENSOR] celsius=");
    Serial.print(celsius, 1);
    Serial.print(" fahrenheit=");
    Serial.println(fahrenheit, 1);

    delay(2000);
}
```

`examples/sensor-debug/validate.py`:
```python
import serial
import time
import sys

PORT = "/dev/ttyUSB0"  # Update to match your port

ser = serial.Serial(PORT, 115200, timeout=1)
time.sleep(3)

results = []
start = time.time()
while time.time() - start < 15 and len(results) < 5:
    line = ser.readline().decode("utf-8", errors="ignore").strip()
    if "[SENSOR]" in line:
        parts = dict(p.split("=") for p in line.split("[SENSOR]")[1].strip().split())
        c = float(parts["celsius"])
        f = float(parts["fahrenheit"])
        expected_f = (c * 9 / 5) + 32
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

`examples/sensor-debug/CLAUDE.md`:
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

**Step 2: Write a test to verify example files exist and validate.py is valid Python**

Add to `tests/test_cli.py` or create `tests/test_examples.py`:
```python
"""Tests for example projects."""

import ast
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


class TestSensorDebugExample:
    def test_ino_file_exists(self):
        assert (EXAMPLES_DIR / "sensor-debug" / "sensor-debug.ino").exists()

    def test_claude_md_exists(self):
        assert (EXAMPLES_DIR / "sensor-debug" / "CLAUDE.md").exists()

    def test_validate_py_exists(self):
        assert (EXAMPLES_DIR / "sensor-debug" / "validate.py").exists()

    def test_validate_py_is_valid_python(self):
        source = (EXAMPLES_DIR / "sensor-debug" / "validate.py").read_text()
        ast.parse(source)  # Raises SyntaxError if invalid

    def test_ino_has_bug(self):
        """The example intentionally has + 23 instead of + 32."""
        source = (EXAMPLES_DIR / "sensor-debug" / "sensor-debug.ino").read_text()
        assert "+ 23" in source
        assert "+ 32" not in source
```

**Step 3: Run tests**

Run: `python -m pytest tests/test_examples.py -v`
Expected: All PASS

**Step 4: Commit**

```bash
git add examples/sensor-debug/ tests/test_examples.py
git commit -m "feat: sensor-debug example with intentional bug"
```

---

### Task 9: Examples — wifi-endpoint and ota-update

**Files:**
- Create: `examples/wifi-endpoint/wifi-endpoint.ino`
- Create: `examples/wifi-endpoint/config.h.example`
- Create: `examples/wifi-endpoint/CLAUDE.md`
- Create: `examples/wifi-endpoint/validate.py`
- Create: `examples/ota-update/ota-update.ino`
- Create: `examples/ota-update/CLAUDE.md`
- Create: `examples/ota-update/validate.py`

**Step 1: Create wifi-endpoint example**

`examples/wifi-endpoint/wifi-endpoint.ino`:
```cpp
#include <WiFi.h>
#include <WebServer.h>
#include "config.h"

WebServer server(80);

void handleHealth() {
    String json = "{\"status\": \"ok\", \"uptime\": " + String(millis()) + "}";
    // BUG: Should be "application/json", not "text/plain"
    server.send(200, "text/plain", json);
}

void setup() {
    Serial.begin(115200);

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.print("[WIFI] Connecting");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    Serial.println("[WIFI] IP:" + WiFi.localIP().toString());

    server.on("/health", handleHealth);
    server.begin();
    Serial.println("[HTTP] server started");
    Serial.println("[READY]");
}

void loop() {
    server.handleClient();
}
```

`examples/wifi-endpoint/config.h.example`:
```cpp
#define WIFI_SSID "YOUR_SSID"
#define WIFI_PASSWORD "YOUR_PASSWORD"
```

`examples/wifi-endpoint/validate.py`:
```python
import serial
import time
import sys
import urllib.request
import json

PORT = "/dev/ttyUSB0"  # Update to match your port

# Read serial to find IP address
ser = serial.Serial(PORT, 115200, timeout=1)
time.sleep(5)

ip = None
start = time.time()
while time.time() - start < 15:
    line = ser.readline().decode("utf-8", errors="ignore").strip()
    if "[WIFI] IP:" in line:
        ip = line.split("IP:")[-1].strip()
        break
ser.close()

if not ip:
    print("[FAIL] Could not find device IP address in serial output.")
    sys.exit(1)

print(f"[INFO] Device IP: {ip}")

# Check /health endpoint
try:
    req = urllib.request.Request(f"http://{ip}/health")
    response = urllib.request.urlopen(req, timeout=5)

    status = response.status
    content_type = response.headers.get("Content-Type", "")
    body = response.read().decode("utf-8")

    print(f"[INFO] Status: {status}")
    print(f"[INFO] Content-Type: {content_type}")
    print(f"[INFO] Body: {body}")

    passed = True

    if status != 200:
        print(f"[FAIL] Expected status 200, got {status}")
        passed = False

    if "application/json" not in content_type:
        print(f"[FAIL] Expected Content-Type 'application/json', got '{content_type}'")
        passed = False

    try:
        json.loads(body)
        print("[PASS] Body is valid JSON")
    except json.JSONDecodeError:
        print("[FAIL] Body is not valid JSON")
        passed = False

    if passed:
        print("\nAll checks passed.")
        sys.exit(0)
    else:
        print(f"\nSome checks failed.")
        sys.exit(1)

except Exception as e:
    print(f"[FAIL] Could not reach device: {e}")
    sys.exit(1)
```

`examples/wifi-endpoint/CLAUDE.md`:
```markdown
# WiFi Endpoint Example

An ESP32 HTTP server that exposes a /health endpoint.

## Expected Behavior
- Connects to WiFi (configure SSID/password in config.h, copy from config.h.example)
- Runs HTTP server on port 80
- GET /health returns `{"status": "ok", "uptime": <millis>}` with Content-Type: application/json

## How to Validate
Run `python validate.py` after flashing. It reads serial to find the IP, then checks:
- /health returns status 200
- Content-Type is application/json
- Response body is valid JSON

## Known Issue
Users report the /health endpoint returns data but some HTTP clients don't parse it correctly as JSON.
```

`examples/ota-update/ota-update.ino`:
```cpp
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoOTA.h>
#include "config.h"

#define VERSION "1.0.0"

WebServer server(80);

void handleVersion() {
    server.send(200, "text/plain", VERSION);
}

void setup() {
    Serial.begin(115200);

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.print("[WIFI] Connecting");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    Serial.println("[WIFI] IP:" + WiFi.localIP().toString());

    ArduinoOTA.setHostname("edesto-ota-demo");
    ArduinoOTA.begin();
    Serial.println("[OTA] ready");

    server.on("/version", handleVersion);
    server.begin();

    Serial.println("[OTA] version=" + String(VERSION));
    Serial.println("[READY]");
}

void loop() {
    ArduinoOTA.handle();
    server.handleClient();
}
```

`examples/ota-update/CLAUDE.md`:
```markdown
# OTA Update Example

An ESP32 with Over-The-Air update support. Change the version string and push wirelessly.

## Expected Behavior
- Connects to WiFi (configure SSID/password in config.h)
- Enables ArduinoOTA for wireless firmware updates
- Prints `[OTA] version=1.0.0` to serial
- GET /version returns current version string

## How to Validate
Run `python validate.py` after flashing. It reads the version from serial output.
After an OTA update, run validate.py again to verify the version changed.

## Task
Update the VERSION string to "1.1.0" and push the update via OTA.
```

`examples/ota-update/validate.py`:
```python
import serial
import time
import sys

PORT = "/dev/ttyUSB0"  # Update to match your port

ser = serial.Serial(PORT, 115200, timeout=1)
time.sleep(5)

version = None
start = time.time()
while time.time() - start < 15:
    line = ser.readline().decode("utf-8", errors="ignore").strip()
    if "[OTA] version=" in line:
        version = line.split("version=")[-1].strip()
        break
ser.close()

if not version:
    print("[FAIL] Could not read version from serial output.")
    sys.exit(1)

print(f"[INFO] Current version: {version}")
print("[PASS] Version string found.")
sys.exit(0)
```

**Step 2: Write tests for examples**

Add to `tests/test_examples.py`:
```python
class TestWifiEndpointExample:
    def test_ino_file_exists(self):
        assert (EXAMPLES_DIR / "wifi-endpoint" / "wifi-endpoint.ino").exists()

    def test_claude_md_exists(self):
        assert (EXAMPLES_DIR / "wifi-endpoint" / "CLAUDE.md").exists()

    def test_validate_py_exists(self):
        assert (EXAMPLES_DIR / "wifi-endpoint" / "validate.py").exists()

    def test_validate_py_is_valid_python(self):
        source = (EXAMPLES_DIR / "wifi-endpoint" / "validate.py").read_text()
        ast.parse(source)

    def test_config_example_exists(self):
        assert (EXAMPLES_DIR / "wifi-endpoint" / "config.h.example").exists()

    def test_ino_has_content_type_bug(self):
        """The example intentionally uses text/plain instead of application/json."""
        source = (EXAMPLES_DIR / "wifi-endpoint" / "wifi-endpoint.ino").read_text()
        assert '"text/plain"' in source
        # The handleHealth should send JSON but with wrong content type
        assert '"application/json"' not in source


class TestOtaUpdateExample:
    def test_ino_file_exists(self):
        assert (EXAMPLES_DIR / "ota-update" / "ota-update.ino").exists()

    def test_claude_md_exists(self):
        assert (EXAMPLES_DIR / "ota-update" / "CLAUDE.md").exists()

    def test_validate_py_exists(self):
        assert (EXAMPLES_DIR / "ota-update" / "validate.py").exists()

    def test_validate_py_is_valid_python(self):
        source = (EXAMPLES_DIR / "ota-update" / "validate.py").read_text()
        ast.parse(source)

    def test_ino_has_version(self):
        source = (EXAMPLES_DIR / "ota-update" / "ota-update.ino").read_text()
        assert '"1.0.0"' in source
```

**Step 3: Run tests**

Run: `python -m pytest tests/test_examples.py -v`
Expected: All PASS

**Step 4: Commit**

```bash
git add examples/ tests/test_examples.py
git commit -m "feat: wifi-endpoint and ota-update examples"
```

---

### Task 10: Final Integration Test and Packaging

**Files:**
- Modify: `tests/test_cli.py`
- Create: `.gitignore` (if not already)
- Create: `LICENSE`

**Step 1: Write integration test**

Add to `tests/test_cli.py`:
```python
class TestIntegration:
    def test_full_workflow(self, runner):
        """Test the full init → read → verify workflow."""
        with runner.isolated_filesystem():
            # Generate CLAUDE.md
            result = runner.invoke(main, ["init", "--board", "esp32", "--port", "/dev/cu.usbserial-0001"])
            assert result.exit_code == 0

            # Verify CLAUDE.md content
            content = Path("CLAUDE.md").read_text()
            assert "# Embedded Development: ESP32" in content
            assert "esp32:esp32:esp32" in content
            assert "/dev/cu.usbserial-0001" in content
            assert "arduino-cli compile" in content
            assert "arduino-cli upload" in content
            assert "Development Loop" in content
            assert "serial.Serial" in content
            assert "[READY]" in content
            assert "ADC2" in content  # ESP32-specific pitfall

            # Verify .cursorrules matches
            assert Path(".cursorrules").read_text() == content

    def test_help_output(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "init" in result.output
        assert "doctor" in result.output
        assert "boards" in result.output
```

**Step 2: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: All PASS

**Step 3: Create LICENSE**

`LICENSE`:
```
MIT License

Copyright (c) 2026 Edesto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Step 4: Final commit**

```bash
git add .
git commit -m "feat: integration tests and MIT license"
```

**Step 5: Verify everything works end-to-end**

```bash
pip install -e .
edesto --help
edesto boards
edesto init --board esp32 --port /dev/ttyUSB0
cat CLAUDE.md
edesto doctor
python -m pytest tests/ -v
```
