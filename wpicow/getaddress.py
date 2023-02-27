from machine import Pin, I2C

port = 0
i2c = I2C(port, sda = Pin(0), scl = Pin(1), freq = 400000)

print("Sensor I2C port: ", port)
print("Sensor I2C address: ", i2c.scan())
