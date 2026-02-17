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
