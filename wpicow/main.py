""" micropython weather station

weather station for micropython
micropython v1.20.0 built 2023-04-26
raspberry pi pico W with RP2040
BME280 environmental sensor
"""

import sys
import gc
from time import sleep
import urlencode
import urequests as requests
import bme280_float as bme280
from machine import Pin, I2C
from config import cfg
from wlanc import wlanc

# weather station variables which are
# set in configuration file config.py

# PORT        = 0     # device I2C port
# ADDRESS     = 119   # device I2C address
# INTERVAL    = 300   # delay between each reading (secs)
# STATION_ID  = "my-station-id"
# STATION_KEY = "my-station-key"
# WU_URL      = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"
# ALTITUDE    = 100   # altitude in feet for barometric pressure correction

def send_data_wu(url,statid,statkey,temp,pres,humid,dewpt):
    """ send sensor data to weather underground """

    values = {
    "action": "updateraw",
    "ID": statid,
    "PASSWORD": statkey,
    "dateutc": "now",
    "tempf": str(temp),
    "baromin": str(pres),
    "humidity": str(humid),
    "dewptf": str(dewpt),
    }

    # build url request string
    urlmod = url + "?"
    postdata = urlencode.urlencode(values)
    urlsum = urlmod + postdata
    req = requests.post(urlsum)
    code = req.status_code
    print("[D] Server status code: ", code)
    if code != 200:
        append_file('[W] Server code:      ', str(code))
    req.close()

def c_to_f(input_temp):
    """ convert Celsius to Farenheit """
    return (input_temp * 1.8) + 32

def pa_to_in(input_pressure):
    """ convert Pa to Inches Hg """
    return input_pressure * 0.0295300

def altitude_cor(input_pressure, alt):
    """ altitude correction factor for pressure measurement """
    alt_cor = (760 - alt * 0.026) / 760
    return input_pressure / alt_cor

def append_file(error_type, error_msg):
    """ append to log file """
    with open('station.log', mode='a', encoding="utf-8") as file:
        file.write(error_type)
        msg=str(error_msg)
        file.write(msg)
        file.write('\n')
        file.close()

def check_file():
    """ check if logfile exists """
    try:
        with open('station.log', mode='r', encoding="utf-8") as file:
            print('[D] station.log found ')
            file.close()
    except OSError:
        with open('station.log', mode='w', encoding="utf-8") as file:
            print('[D] station.log created ')
            file.write("WuPicoWether logfile")
            file.close()

def main():
    """ read sensor """

    print('[D] WuPicoWeather starting ')
    try:
        while True:
            # retrieve sensor data
            sensor = bme280.BME280(i2c=i2c, address=ADDRESS)
            data = sensor.read_compensated_data()
            temp_raw = data[0]
            pres_raw = data[1]
            humid_raw = data[2]
            dewpoint_raw = sensor.dew_point

            # apply conversions
            dewpoint_f = round(c_to_f(dewpoint_raw), 3)
            temp_f = round(c_to_f(temp_raw), 3)
            pres_in = pa_to_in(pres_raw/100)
            pres_in_cor = round(altitude_cor(pres_in, ALTITUDE), 3)
            humid = round(humid_raw, 3)

            # uncomment for debugging
            #print("Temp = ",temp_f)
            #print("Pres = ",pres_in_cor)
            #print("Humi = ",humid)
            #print("Dewp = ",dewpoint_f,"\n")

            # send data to weather underground
            send_data_wu(WU_URL,STATION_ID,STATION_KEY,temp_f,pres_in_cor,humid,dewpoint_f)

            # wait for next reading
            for _ in range(INTERVAL):
                led.on()
                sleep(.5)
                led.off()
                sleep(.5)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt, exiting")
        led.off()
        sys.exit(0)

    except MemoryError as error:
        print("\n[E] Memory error: ")
        print(error)
        print('[E] Memory allocated: ',gc.mem_alloc())
        print('[E] Memory free: ',gc.mem_free())
        append_file('[E] MemoryError:      ', error)
        append_file('[E] Memory allocated: ',gc.mem_alloc())
        append_file('[E] Memory free:      ',gc.mem_free())
        gc.collect()
        sleep(INTERVAL)
        #sys.exit(1)

    except OSError as error:
        print("\n[E] OSError: ")
        print(error)
        append_file('[E] OSError:          ', error)
        sleep(INTERVAL)
        #sys.exit(1)

    except RuntimeError as error:
        print("\n[E] RuntimeError: ")
        print(error)
        append_file('[E] RuntimeError:     ', error)
        sleep(INTERVAL)
        #sys.exit(1)

if __name__=="__main__":
    try:
        # configuration variables
        PORT         = int(cfg["station"]["port"])
        ADDRESS      = int(cfg["station"]["address"])
        INTERVAL     = int(cfg["station"]["interval"])
        STATION_ID   = cfg["station"]["station_id"]
        STATION_KEY  = cfg["station"]["station_key"]
        WU_URL       = cfg["station"]["wu_url"]
        ALTITUDE     = int(cfg["station"]["altitude"])

        # hardware setup
        i2c = I2C(PORT, sda = Pin(0), scl = Pin(1), freq = 400000)
        led = Pin('LED', Pin.OUT)
        wlanc (cfg["wlan"]["ssid"], cfg["wlan"]["pswd"])

        check_file()
        main()

    except KeyboardInterrupt:
        print("\nKeyboard interrupt, exiting")
        led.off()
        sys.exit(0)
