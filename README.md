# edesto-dev

**You already have Claude Code. Here's how to use it for embedded development.**

AI coding agents stop at the terminal. `edesto init` teaches them how to compile, flash, and validate firmware on your actual hardware. No extra subscriptions. No cloud. No datasheets leaving your machine.



https://github.com/user-attachments/assets/ac59418e-fce9-466f-a85b-55b28294fcc9



## Install

```
pipx install edesto-dev
```

## Quick Start

```bash
# 1. Plug in your board and run:
edesto init

# 2. Open Claude Code in the same directory:
claude

# 3. Tell it what to do:
# "The sensor readings are wrong. Find and fix the bug."
```

That's it. `edesto init` auto-detects your board and serial port via `arduino-cli`. Claude Code reads the generated `CLAUDE.md`, writes firmware, flashes it to your board, reads serial output to verify it works, and iterates until it's correct.

You can also specify the board and port manually:

```bash
edesto init --board esp32 --port /dev/cu.usbserial-0001
```

## How It Works

`edesto init` generates a `CLAUDE.md` that gives your AI agent the full development loop:

1. **Edit** code (.ino, .cpp, .h files)
2. **Compile** with `arduino-cli`
3. **Flash** to the board over USB
4. **Validate** by reading serial output from the device
5. **Iterate** if validation fails

The validation step is what makes this work. The `CLAUDE.md` teaches Claude Code serial conventions (`[READY]`, `[ERROR]`, `[SENSOR] key=value`) and gives it a Python snippet to read device output. The agent verifies its own changes on real hardware.

If you have any datasheets, just drop them into `./datasheets` and Claude will find them. You can also just leave them anywhere in the directory.

## Commands

```bash
edesto init                                 # Auto-detect board and port, generate CLAUDE.md
edesto init --board esp32                   # Specify board, auto-detect port
edesto init --board esp32 --port /dev/ttyUSB0  # Fully manual
edesto boards                               # List supported boards
edesto doctor                               # Check your environment
```

## Supported Boards

| Slug | Board | FQBN |
|------|-------|------|
| `esp32` | ESP32 | `esp32:esp32:esp32` |
| `esp32s3` | ESP32-S3 | `esp32:esp32:esp32s3` |
| `esp32c3` | ESP32-C3 | `esp32:esp32:esp32c3` |
| `esp32c6` | ESP32-C6 | `esp32:esp32:esp32c6` |
| `esp8266` | ESP8266 | `esp8266:esp8266:nodemcuv2` |
| `arduino-uno` | Arduino Uno | `arduino:avr:uno` |
| `arduino-nano` | Arduino Nano | `arduino:avr:nano` |
| `arduino-mega` | Arduino Mega 2560 | `arduino:avr:mega` |
| `rp2040` | Raspberry Pi Pico | `rp2040:rp2040:rpipico` |
| `teensy40` | Teensy 4.0 | `teensy:avr:teensy40` |
| `teensy41` | Teensy 4.1 | `teensy:avr:teensy41` |
| `stm32-nucleo` | STM32 Nucleo-64 | `STMicroelectronics:stm32:Nucleo_64` |

## Examples

Three example projects in `examples/`, each with an intentional bug for Claude Code to find and fix:

### sensor-debug
A temperature sensor sketch with a unit conversion bug. Celsius values are correct but Fahrenheit readings are off. Claude Code reads serial output, spots the math error, fixes it, and validates.

### wifi-endpoint
An ESP32 HTTP server where the `/health` endpoint returns JSON but with the wrong Content-Type header. Claude Code makes HTTP requests to the device to validate the fix.

### ota-update
An ESP32 with OTA support. Claude Code updates the version string and pushes firmware wirelessly, then verifies the new version via serial.

## Prerequisites

- [arduino-cli](https://arduino.github.io/arduino-cli/installation/) installed
- A supported board connected via USB
- Python 3.10+

Run `edesto doctor` to check your setup.

## About

Built by [Edesto](https://edesto.com). We build tools for robotics and embedded teams.
