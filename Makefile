VENV     = .venv
PYTHON  ?= python3
PIP      = $(VENV)/bin/pip
MPREMOTE = $(VENV)/bin/mpremote
ESPTOOL  = $(VENV)/bin/esptool.py

# Auto-detect the ESP32-C6 serial port (macOS: cu.usbserial/usbmodem, Linux: ttyUSB/ttyACM)
PORT ?= $(shell ls /dev/cu.usbserial-* /dev/cu.SLAB_USBtoUART /dev/cu.usbmodem* \
                  /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -1)

# MicroPython firmware — override with: make flash-firmware FIRMWARE=your.bin
# Latest releases: https://micropython.org/download/ESP32_GENERIC_C6/
FIRMWARE_URL ?= https://micropython.org/resources/firmware/ESP32_GENERIC_C6-20241129-v1.24.1.bin
FIRMWARE     ?= esp32c6-micropython.bin

.PHONY: all install setup flash-firmware erase-flash download-firmware \
        deploy repl reset ls clean check-port check-firmware

# ── First-time setup ──────────────────────────────────────────────────────────

all: deploy

# Create the venv (once); used as a prerequisite by install
$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)

install: $(VENV)/bin/activate
	$(PIP) install --upgrade mpremote esptool

# Full first-time flow: create venv, install tools, download firmware, flash it
setup: install download-firmware erase-flash flash-firmware
	@echo ""
	@echo "MicroPython is now installed. Run 'make deploy' to copy your code."

# ── Firmware flashing ─────────────────────────────────────────────────────────

download-firmware:
	@echo "Downloading MicroPython firmware..."
	curl -L -o $(FIRMWARE) $(FIRMWARE_URL)
	@echo "Saved to $(FIRMWARE)"

check-firmware:
	@if [ ! -f "$(FIRMWARE)" ]; then \
		echo "ERROR: Firmware file '$(FIRMWARE)' not found."; \
		echo "       Run 'make download-firmware' or set FIRMWARE=path/to/your.bin"; \
		exit 1; \
	fi

erase-flash: check-port
	@echo "Erasing ESP32-C6 flash on $(PORT)..."
	$(ESPTOOL) --chip esp32c6 --port $(PORT) erase-flash

flash-firmware: check-port check-firmware
	@echo "Flashing MicroPython firmware from $(FIRMWARE) to $(PORT)..."
	$(ESPTOOL) --chip esp32c6 --port $(PORT) --baud 460800 \
		write_flash -z 0x0 $(FIRMWARE)

# ── Code deployment ───────────────────────────────────────────────────────────

deploy: check-port
	$(MPREMOTE) connect $(PORT) cp bme280.py :bme280.py + cp main.py :main.py + reset

repl: check-port
	$(MPREMOTE) connect $(PORT) repl

reset: check-port
	$(MPREMOTE) connect $(PORT) reset

ls: check-port
	$(MPREMOTE) connect $(PORT) ls

# ── Helpers ───────────────────────────────────────────────────────────────────

check-port:
	@if [ -z "$(PORT)" ]; then \
		echo "ERROR: No ESP32-C6 serial port found. Is the board plugged in?"; \
		echo "       Override with: make <target> PORT=/dev/cu.your-port"; \
		exit 1; \
	fi
	@echo "Using port: $(PORT)"

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	rm -f $(FIRMWARE)
	rm -rf $(VENV)
