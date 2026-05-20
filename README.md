# ESP32 BME280 Test

Blinks the built-in LED and reads temperature, pressure, and humidity from a
PiicoDev Atmospheric Sensor (BME280) over I2C, printing values to the USB serial console.

## Hardware

| Signal | ESP32 pin |
|--------|-----------|
| SDA    | GPIO 21   |
| SCL    | GPIO 22   |
| LED    | GPIO 2 (built-in) |

The BME280 I2C address defaults to `0x77` (PiicoDev default).

## First-time setup

Install tools, flash MicroPython, and deploy code in one go:

```sh
make install   # install mpremote and esptool (Python tools)
make setup     # download MicroPython firmware, erase flash, flash firmware
make deploy    # copy bme280.py + main.py to the board and reboot
```

Then open the serial console to see live readings:

```sh
make repl
```

Example output:
```
Temp: 23.4 C  |  Pressure: 1013.2 hPa  |  Humidity: 55.3 %
```

Press `Ctrl+]` to exit the REPL.

## Subsequent deploys

After MicroPython is installed, only `make deploy` is needed when you change the code.

## Other make targets

| Target | Description |
|--------|-------------|
| `make install` | Install mpremote and esptool via pip |
| `make setup` | Full first-time flash (download firmware → erase → flash) |
| `make download-firmware` | Download MicroPython .bin only |
| `make erase-flash` | Wipe the ESP32 flash |
| `make flash-firmware` | Burn MicroPython firmware |
| `make deploy` | Copy code to board and reset |
| `make repl` | Open serial console |
| `make reset` | Reboot the board |
| `make ls` | List files on the board |
| `make clean` | Remove .pyc files and downloaded firmware |

## Overriding the serial port

The port is auto-detected. If detection fails or you have multiple boards connected:

```sh
make deploy PORT=/dev/ttyUSB0          # Linux
make deploy PORT=/dev/cu.usbserial-0001 # macOS
```

## Linux permission fix

If you get a permission denied error on the serial port:

```sh
sudo usermod -aG dialout $USER
# log out and back in for it to take effect
```

## Using a different firmware

```sh
make flash-firmware FIRMWARE=~/Downloads/ESP32_GENERIC-v1.24.1.bin
```

Latest firmware releases: https://micropython.org/download/ESP32_GENERIC/
