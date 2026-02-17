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


# --- ESP32 ---

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


# --- ESP32-S3 ---

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
        "GPIO 48: RGB LED (WS2812-style, not a simple HIGH/LOW LED)",
        "GPIO 19/20: USB D-/D+ — do not use for general I/O",
        "GPIO 0: Boot button — do not use for general I/O",
        "ADC1: GPIO 1-10 (works alongside WiFi)",
        "ADC2: GPIO 11-20 (does NOT work when WiFi is active)",
        "I2C default: SDA=8, SCL=9",
        "SPI default: MOSI=11, MISO=13, SCK=12, SS=10",
    ],
    pitfalls=[
        "ADC2 pins do not work when WiFi is active. Use ADC1 pins (1-10) if you need analog reads with WiFi.",
        "GPIO 19/20 are USB pins. Do not use them for general I/O.",
        "RGB LED on GPIO 48 requires NeoPixel-style protocol, not simple digitalWrite.",
        "If upload fails, hold BOOT and press RST, then release BOOT after upload starts.",
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


# --- ESP32-C3 ---

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
        "GPIO 8: Onboard LED",
        "GPIO 9: Boot button — do not use for general I/O",
        "Only 22 GPIO pins available",
        "ADC1: GPIO 0-4 (no ADC2 on this chip)",
        "RISC-V single core architecture",
    ],
    pitfalls=[
        "Single-core RISC-V — no dual-core parallelism available.",
        "Only 22 GPIO pins. Plan pin usage carefully.",
        "GPIO 8 is shared between onboard LED and I2C SDA. Use a different SDA pin if LED is needed.",
        "GPIO 9 is the BOOT button. Do not use for general I/O.",
        "delay() blocks the entire core. Use millis() for non-blocking timing.",
        "No Bluetooth Classic — only BLE is supported.",
    ],
    includes={
        "wifi": "#include <WiFi.h>",
        "http_server": "#include <WebServer.h>",
        "ota": "#include <ArduinoOTA.h>",
        "preferences": "#include <Preferences.h>",
        "spiffs": "#include <SPIFFS.h>",
    },
))


# --- ESP32-C6 ---

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
        "GPIO 8: Onboard LED",
        "GPIO 9: Boot button — do not use for general I/O",
        "30 GPIO pins available",
        "ADC1: GPIO 0-6",
        "RISC-V architecture",
        "IEEE 802.15.4 radio for Zigbee/Thread",
    ],
    pitfalls=[
        "Single high-performance RISC-V core — no dual-core parallelism.",
        "WiFi 6 support requires ESP-IDF v5.1+ (check your Arduino core version).",
        "Zigbee and Thread share the 802.15.4 radio — cannot use both simultaneously.",
        "GPIO 9 is the BOOT button. Do not use for general I/O.",
        "delay() blocks the entire core. Use millis() for non-blocking timing.",
        "No Bluetooth Classic — only BLE is supported.",
        "Newer chip — verify your Arduino ESP32 core version supports it.",
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
        "GPIO 2: Onboard LED (active LOW — LOW turns it ON)",
        "GPIO 0: Flash/boot mode — do not use for general I/O",
        "GPIO 16: Deep sleep wake — connect to RST for deep sleep wake-up",
        "1 ADC pin (A0), 10-bit resolution, 0-1V range",
        "I2C default: SDA=4 (D2), SCL=5 (D1)",
        "NodeMCU D-labels differ from GPIO numbers (D1=GPIO5, D2=GPIO4, etc.)",
    ],
    pitfalls=[
        "Only 80KB RAM — avoid large buffers and dynamic memory allocation.",
        "Single core — delay() blocks WiFi stack. Use yield() or millis()-based timing.",
        "GPIO 6-11 are connected to flash. Do not use them.",
        "Onboard LED is active LOW — digitalWrite(2, LOW) turns it ON.",
        "ADC range is 0-1V (not 3.3V). Use a voltage divider for higher voltages.",
        "Watchdog timer will reset the chip if loop() takes too long. Use yield() in long operations.",
        "2.4GHz WiFi only — no 5GHz support.",
    ],
    includes={
        "wifi": "#include <ESP8266WiFi.h>",
        "http_server": "#include <ESP8266WebServer.h>",
        "ota": "#include <ArduinoOTA.h>",
        "spiffs": "#include <FS.h>",
    },
))


# --- Arduino Uno ---

_register(Board(
    slug="arduino-uno",
    name="Arduino Uno",
    fqbn="arduino:avr:uno",
    core="arduino:avr",
    core_url="",
    baud_rate=9600,
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
        "A0-A5: 10-bit analog input",
        "PWM: pins 3, 5, 6, 9, 10, 11",
        "I2C: SDA=A4, SCL=A5",
        "Pin 13 flickers during SPI communication",
        "Pins 0/1: Serial TX/RX (shared with USB)",
    ],
    pitfalls=[
        "Only 2KB SRAM and 32KB flash. Avoid String objects and large arrays.",
        "No floating-point hardware — float operations are slow and use flash.",
        "Pin 13 is shared with SPI SCK. LED flickers during SPI communication.",
        "Pins 0/1 are shared with USB serial. Do not use for I/O during serial communication.",
        "analogWrite() is PWM, not true analog output. No DAC available.",
        "External interrupts only on pins 2 and 3.",
        "delay() blocks the entire MCU. Use millis() for non-blocking timing.",
        "No WiFi or Bluetooth. Use external modules (ESP-01, HC-05) if needed.",
    ],
    includes={},
))


# --- Arduino Nano ---

_register(Board(
    slug="arduino-nano",
    name="Arduino Nano",
    fqbn="arduino:avr:nano",
    core="arduino:avr",
    core_url="",
    baud_rate=9600,
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
        "GPIO 13: Onboard LED",
        "A0-A7: analog input (A6/A7 are analog input only, no digital)",
        "PWM: pins 3, 5, 6, 9, 10, 11",
        "I2C: SDA=A4, SCL=A5",
        "Pins 0/1: Serial TX/RX (shared with USB)",
    ],
    pitfalls=[
        "Only 2KB SRAM and 32KB flash. Avoid String objects and large arrays.",
        "A6/A7 are analog input only — cannot be used as digital I/O.",
        "Clone Nanos often need old bootloader: use --fqbn arduino:avr:nano:cpu=atmega328old.",
        "No floating-point hardware — float operations are slow and use flash.",
        "Pins 0/1 are shared with USB serial. Do not use for I/O during serial communication.",
        "External interrupts only on pins 2 and 3.",
        "delay() blocks the entire MCU. Use millis() for non-blocking timing.",
        "No WiFi or Bluetooth. Use external modules if needed.",
    ],
    includes={},
))


# --- Arduino Mega 2560 ---

_register(Board(
    slug="arduino-mega",
    name="Arduino Mega 2560",
    fqbn="arduino:avr:mega",
    core="arduino:avr",
    core_url="",
    baud_rate=9600,
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
        "A0-A15: 16 analog input channels, 10-bit",
        "PWM: pins 2-13, 44-46",
        "I2C: SDA=20, SCL=21",
        "SPI: MOSI=51, MISO=50, SCK=52, SS=53",
        "4 serial ports: Serial (0/1), Serial1 (18/19), Serial2 (16/17), Serial3 (14/15)",
        "External interrupts: pins 2, 3, 18, 19, 20, 21",
    ],
    pitfalls=[
        "8KB SRAM and 256KB flash — more than Uno but still limited.",
        "No floating-point hardware — float operations are slow.",
        "SPI is on pins 50-53, NOT 11-13 like Uno. Code from Uno examples must be adapted.",
        "Pin 53 (SS) must be set as OUTPUT even if not used, or SPI will not work.",
        "analogWrite() is PWM, not true analog output. No DAC available.",
        "delay() blocks the entire MCU. Use millis() for non-blocking timing.",
        "No WiFi or Bluetooth. Use external modules if needed.",
    ],
    includes={},
))


# --- Raspberry Pi Pico (RP2040) ---

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
        "ADC: GPIO 26-28 (12-bit) + GPIO 29 (VSYS/3 voltage monitor)",
        "All GPIO pins support PWM",
        "I2C0: SDA=4, SCL=5 | I2C1: SDA=6, SCL=7",
        "SPI0: MOSI=19, MISO=16, SCK=18, SS=17 | SPI1: MOSI=15, MISO=12, SCK=14, SS=13",
        "UART0: TX=0, RX=1 | UART1: TX=8, RX=9",
        "2 PIO (Programmable I/O) blocks for custom protocols",
    ],
    pitfalls=[
        "264KB SRAM and 2MB flash. Adequate for most projects but plan large buffers carefully.",
        "First upload requires BOOTSEL mode — hold BOOTSEL while plugging in USB.",
        "Pico W has LED on different pin (via CYW43 WiFi chip). This definition is for Pico (non-W).",
        "ADC has known offset error. Calibrate if precision is needed.",
        "USB Serial is separate from UART. Serial is USB, Serial1/Serial2 are UART.",
        "No EEPROM — use LittleFS for persistent storage.",
        "delay() only blocks the current core. Use millis() for non-blocking timing.",
        "Dual core: use setup1()/loop1() for second core tasks.",
    ],
    includes={},
))


# --- Teensy 4.0 ---

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
        "14 ADC pins, 12-bit resolution",
        "PWM on many pins",
        "3 I2C buses",
        "2 SPI buses",
        "7 UART serial ports",
        "CAN bus support",
        "Native USB",
    ],
    pitfalls=[
        "Upload uses teensy_loader_cli, not standard serial upload.",
        "USB CDC — baud rate setting is ignored (always full USB speed).",
        "600MHz ARM Cortex-M7 runs hot. Consider heat management for sustained loads.",
        "1024KB flash, 512KB RAM — generous but not unlimited.",
        "No WiFi or Bluetooth. Use external modules if needed.",
        "Program button for bootloader mode.",
        "Use analogReadResolution(12) to get full 12-bit ADC resolution.",
        "Use elapsedMillis/elapsedMicros for non-blocking timing.",
    ],
    includes={},
))


# --- Teensy 4.1 ---

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
        "18 ADC pins",
        "PWM on many pins",
        "3 I2C buses",
        "2 SPI buses",
        "8 UART serial ports",
        "Native Ethernet (requires MagJack soldering)",
        "SD card via SDIO (bottom side)",
        "USB host support",
        "Optional PSRAM (solder pads on bottom)",
    ],
    pitfalls=[
        "Upload uses teensy_loader_cli, not standard serial upload.",
        "USB CDC — baud rate setting is ignored (always full USB speed).",
        "Ethernet requires soldering a MagJack connector to the board.",
        "SD card slot is on the bottom — use BUILTIN_SDCARD constant.",
        "PSRAM uses EXTMEM keyword for allocation.",
        "8MB flash — much more than Teensy 4.0.",
        "Program button for bootloader mode.",
        "Use elapsedMillis/elapsedMicros for non-blocking timing.",
    ],
    includes={},
))


# --- STM32 Nucleo-64 ---

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
        "LD2 on PA5/D13",
        "B1 user button on PC13",
        "Arduino-compatible headers: D0-D15, A0-A5",
        "ADC: 12-bit resolution",
        "DAC available on some variants",
        "I2C: D14 (SDA), D15 (SCL)",
        "SPI: D11 (MOSI), D12 (MISO), D13 (SCK)",
        "UART via ST-Link Virtual COM Port (VCP)",
    ],
    pitfalls=[
        "Nucleo-64 is a family — many chip variants exist. Verify your specific board variant.",
        "Upload is via ST-Link, not USB serial. Install ST-Link drivers.",
        "Serial output is via ST-Link VCP, not native USB serial.",
        "Arduino pin mapping differs from STM32 native pin names (PA0, PB3, etc.).",
        "Library compatibility varies — not all Arduino libraries work with STM32.",
        "Flash and RAM sizes vary by chip variant.",
        "ST-Link drivers required on Windows.",
        "delay() blocks. Use millis() or HAL_GetTick() for non-blocking timing.",
    ],
    includes={},
))
