from machine import Pin, I2C
import time
from bme280 import BME280

# GPIO2 is the built-in LED on most ESP32 dev boards (active HIGH)
LED_PIN = 2

# Default I2C pins on ESP32: SDA=21, SCL=22
I2C_SDA = 21
I2C_SCL = 22

led = Pin(LED_PIN, Pin.OUT)
i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400_000)

print("Scanning I2C bus...")
devices = i2c.scan()
print("Found:", ["0x{:02X}".format(d) for d in devices])

sensor = BME280(i2c)
print("BME280 ready\n")

while True:
    led.value(1)
    time.sleep_ms(100)
    led.value(0)

    temp, pressure, humidity = sensor.read()
    print("Temp: {:.1f} C  |  Pressure: {:.1f} hPa  |  Humidity: {:.1f} %".format(
        temp, pressure, humidity))

    time.sleep(2)
