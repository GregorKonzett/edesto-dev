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
