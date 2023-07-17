""" verifysensor.py

verify bme280 sensor on i2c bus
"""

import sys
from time import sleep
from machine import Pin, I2C
import bme280_float as bme280

ADDRESS = 119
REPEAT = 3
INTERVAL = 10

i2c=I2C(0,sda=Pin(0), scl=Pin(1), freq=100000)
led = Pin('LED', Pin.OUT)
sleep(1)

try:
    #while True:
    for i in range(REPEAT):
        bme=bme280.BME280(i2c=i2c, address=ADDRESS)
        print(bme.values)
        #sleep(10)
        for j in range(INTERVAL):
            led.on()
            sleep(0.5)
            led.off()
            sleep(0.5)

except OSError as error:
    print("\nOSError, exiting")
    print(error)
    led.off()
    sys.exit(1)

except RuntimeError as error:
    print("\nRuntimeError, exiting")
    print(error)
    led.off()
    sys.exit(1)

except KeyboardInterrupt:
    print("Keyboard interrupt, program stopped")
    led.off()
    sys.exit(0)
