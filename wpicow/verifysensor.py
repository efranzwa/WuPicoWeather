import sys
from machine import Pin, I2C
from time import sleep
import bme280_float as bme280

address = 119
i2c=I2C(0,sda=Pin(0), scl=Pin(1), freq=100000)
led = Pin('LED', Pin.OUT)
sleep(1)
repeat = 3
interval = 10

try:
    #while True:
    for i in range(repeat):
        bme=bme280.BME280(i2c=i2c, address=address)
        print(bme.values)
        #sleep(10)
        for j in range(interval):
            led.on()
            sleep(0.5)
            led.off()
            sleep(0.5)

except Exception as error:
    print("\nException, exiting")
    print(error)
    led.off()
    sys.exit(1)

except KeyboardInterrupt:
    print("Keyboard interrupt, program stopped")
    led.off()
    sys.exit(0)
