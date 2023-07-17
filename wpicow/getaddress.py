""" getaddress.py

module to check device address on i2c bus
"""

from machine import Pin, I2C

PORT = 0
i2c = I2C(PORT, sda = Pin(0), scl = Pin(1), freq = 400000)

print("Sensor I2C port: ", PORT)
print("Sensor I2C address: ", i2c.scan())
