import struct
from machine import I2C

BME280_I2C_ADDR = 0x77  # PiicoDev default; try 0x76 if not found

_REG_ID       = 0xD0
_REG_RESET    = 0xE0
_REG_CTRL_HUM = 0xF2
_REG_STATUS   = 0xF3
_REG_CTRL_MEAS = 0xF4
_REG_CONFIG   = 0xF5
_REG_DATA     = 0xF7
_REG_CALIB1   = 0x88
_REG_CALIB2   = 0xE1

OVERSAMPLING_1 = 1
OVERSAMPLING_2 = 2
OVERSAMPLING_4 = 3
OVERSAMPLING_8 = 4
OVERSAMPLING_16 = 5
MODE_NORMAL = 3


class BME280:
    def __init__(self, i2c, addr=BME280_I2C_ADDR):
        self._i2c = i2c
        self._addr = addr
        if self._read_byte(_REG_ID) != 0x60:
            raise RuntimeError("BME280 not found at address 0x{:02X}".format(addr))
        self._load_calibration()
        # humidity x1, temp x2, pressure x2, normal mode
        self._write_byte(_REG_CTRL_HUM, OVERSAMPLING_1)
        self._write_byte(_REG_CTRL_MEAS,
                         (OVERSAMPLING_2 << 5) | (OVERSAMPLING_2 << 2) | MODE_NORMAL)

    def _read_byte(self, reg):
        return self._i2c.readfrom_mem(self._addr, reg, 1)[0]

    def _read_bytes(self, reg, n):
        return self._i2c.readfrom_mem(self._addr, reg, n)

    def _write_byte(self, reg, val):
        self._i2c.writeto_mem(self._addr, reg, bytes([val]))

    def _load_calibration(self):
        c = self._read_bytes(_REG_CALIB1, 24)
        self._T1, self._T2, self._T3 = struct.unpack_from("<HhH", c, 0)[0], \
            struct.unpack_from("<hH", c, 2)[0], struct.unpack_from("<h", c, 4)[0]
        self._P = list(struct.unpack_from("<Hhhhhhhhh", c, 6))
        self._H1 = self._read_byte(0xA1)
        c2 = self._read_bytes(_REG_CALIB2, 7)
        self._H2 = struct.unpack_from("<h", c2, 0)[0]
        self._H3 = c2[2]
        self._H4 = (c2[3] << 4) | (c2[4] & 0x0F)
        self._H5 = (c2[5] << 4) | (c2[4] >> 4)
        self._H6 = struct.unpack_from("<b", c2, 6)[0]
        # sign-extend H4/H5
        if self._H4 > 2047: self._H4 -= 4096
        if self._H5 > 2047: self._H5 -= 4096

    def read(self):
        d = self._read_bytes(_REG_DATA, 8)
        raw_p = (d[0] << 12) | (d[1] << 4) | (d[2] >> 4)
        raw_t = (d[3] << 12) | (d[4] << 4) | (d[5] >> 4)
        raw_h = (d[6] << 8) | d[7]

        # Temperature compensation (yields t_fine used by P and H)
        var1 = (raw_t / 16384.0 - self._T1 / 1024.0) * self._T2
        var2 = (raw_t / 131072.0 - self._T1 / 8192.0) ** 2 * self._T3
        t_fine = var1 + var2
        temperature = t_fine / 5120.0

        # Pressure compensation
        var1 = t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * self._P[5] / 32768.0
        var2 += var1 * self._P[4] * 2.0
        var2 = var2 / 4.0 + self._P[3] * 65536.0
        var1 = (self._P[2] * var1 * var1 / 524288.0 + self._P[1] * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self._P[0]
        if var1 == 0:
            pressure = 0
        else:
            pressure = 1048576.0 - raw_p
            pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
            var1 = self._P[8] * pressure * pressure / 2147483648.0
            var2 = pressure * self._P[7] / 32768.0
            pressure += (var1 + var2 + self._P[6]) / 16.0
            pressure /= 100.0  # hPa

        # Humidity compensation
        h = t_fine - 76800.0
        if h == 0:
            humidity = 0
        else:
            h = (raw_h - (self._H4 * 64.0 + self._H5 / 16384.0 * h)) * \
                (self._H2 / 65536.0 * (1.0 + self._H6 / 67108864.0 * h *
                 (1.0 + self._H3 / 67108864.0 * h)))
            humidity = h * (1.0 - self._H1 * h / 524288.0)
            humidity = max(0.0, min(100.0, humidity))

        return temperature, pressure, humidity
