# edesto-dev Design

## What

CLI tool that generates CLAUDE.md files for embedded development. One command (`edesto init`) teaches Claude Code the full write → flash → validate loop for your hardware.

## Decisions

- **Toolchain:** arduino-cli only
- **OS support:** macOS + Linux (Unix serial paths)
- **Validation:** Serial only in v1. All boards print structured output, Claude Code reads it via pyserial.
- **No HTTP/MQTT/BLE validation** in v1 — serial is universal and sufficient.

## Supported Boards (13)

**ESP32 family** (esp32:esp32:* core):
- esp32 (FQBN: esp32:esp32:esp32)
- esp32s3 (FQBN: esp32:esp32:esp32s3)
- esp32c3 (FQBN: esp32:esp32:esp32c3)
- esp32c6 (FQBN: esp32:esp32:esp32c6)

**ESP8266** (esp8266:esp8266:* core):
- esp8266 (FQBN: esp8266:esp8266:nodemcuv2)

**Arduino AVR** (arduino:avr:* core):
- arduino-uno (FQBN: arduino:avr:uno)
- arduino-nano (FQBN: arduino:avr:nano)
- arduino-mega (FQBN: arduino:avr:mega)

**RP2040** (rp2040:rp2040:* core):
- rp2040 (FQBN: rp2040:rp2040:rpipico)

**Teensy** (teensy:avr:* core):
- teensy40 (FQBN: teensy:avr:teensy40)
- teensy41 (FQBN: teensy:avr:teensy41)

**STM32** (STMicroelectronics:stm32:* core):
- stm32-nucleo (FQBN: STMicroelectronics:stm32:Nucleo_64)

## Architecture

```
edesto_dev/
├── __init__.py           # Version string
├── cli.py                # Click CLI: init, doctor, boards
├── boards.py             # Board definitions and detection
└── templates/
    ├── esp32.md          # Shared by esp32, esp32s3, esp32c3, esp32c6
    ├── esp8266.md
    ├── arduino_uno.md
    ├── arduino_nano.md
    ├── arduino_mega.md
    ├── rp2040.md
    ├── teensy.md         # Shared by teensy40, teensy41
    └── stm32_nucleo.md
```

## Validation Approach

Serial only. Every board template instructs Claude Code to:
1. Write firmware that prints structured serial output
2. Flash via arduino-cli upload
3. Read serial via pyserial Python snippet
4. Parse structured tags: [READY], [ERROR], [SENSOR], etc.
5. Determine pass/fail from parsed output

## Serial Conventions

All templates teach these conventions:
- `Serial.begin(115200)` in setup()
- `Serial.println()` for complete lines
- `[READY]` when initialization complete
- `[ERROR] description` for failures
- `[SENSOR] key=value` for data
- Board-specific tags as needed

## CLI Commands

- `edesto init [--board NAME]` — detect board + generate CLAUDE.md
- `edesto doctor` — check arduino-cli, cores, serial port, permissions
- `edesto boards` — list supported boards and detected devices

## Tech Stack

Python 3.10+, click, pyserial. No other dependencies.
