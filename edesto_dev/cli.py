"""CLI entry point for edesto-dev."""

import glob as globmod
import shutil
import subprocess
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
    click.echo("Also created .cursorrules for Cursor users.")


@main.command()
def boards():
    """List supported boards."""
    board_list = list_boards()
    click.echo(f"Supported boards ({len(board_list)}):\n")
    click.echo(f"  {'Slug':<20} {'Name':<30} {'FQBN'}")
    click.echo(f"  {'─' * 20} {'─' * 30} {'─' * 40}")
    for b in board_list:
        click.echo(f"  {b.slug:<20} {b.name:<30} {b.fqbn}")


@main.command()
def doctor():
    """Check your environment for embedded development."""
    ok = True

    # Check arduino-cli
    arduino_cli = shutil.which("arduino-cli")
    if arduino_cli:
        click.echo(f"[OK] arduino-cli found: {arduino_cli}")
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
        click.echo("[OK] Serial ports found:")
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
