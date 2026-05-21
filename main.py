from machine import Pin, I2C
import neopixel
import time
from bme280 import BME280

# SparkFun Thing Plus - ESP32-C6: RGB NeoPixel on IO23
RGB_PIN = 23
WHITE = (255, 255, 255)
OFF   = (0, 0, 0)

# I2C pins — ESP32-C6 routes I2C via GPIO matrix; any free GPIO works
I2C_SDA = 21
I2C_SCL = 22

rgb = neopixel.NeoPixel(Pin(RGB_PIN), 1)
i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400_000)

print("Scanning I2C bus...")
devices = i2c.scan()
print("Found:", ["0x{:02X}".format(d) for d in devices])

sensor = BME280(i2c)
print("BME280 ready\n")

while True:
    rgb[0] = WHITE
    rgb.write()
    time.sleep_ms(100)
    rgb[0] = OFF
    rgb.write()

    temp, pressure, humidity = sensor.read()
    print("Temp: {:.1f} C  |  Pressure: {:.1f} hPa  |  Humidity: {:.1f} %".format(
        temp, pressure, humidity))

    time.sleep(2)
