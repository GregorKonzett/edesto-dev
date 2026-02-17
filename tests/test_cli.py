"""Tests for the edesto CLI."""

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
        assert "not found" in result.output.lower() or "not installed" in result.output.lower()
