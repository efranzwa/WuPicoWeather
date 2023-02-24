'''
    weather station for micropython
    micropython v1.19.1 built 2022-12-20
    raspberry pi pico W with RP2040
'''

import urlencode
import sys
import urequests as requests
import bme280_float as bme280
from time import sleep
from machine import Pin, I2C
from config import cfg
from wlanc import wlanc

'''
weather station variables which are
set in configuration file config.py

PORT        = 0     # device I2C port
ADDRESS     = 77    # device I2C address
INTERVAL    = 300   # delay between each reading (secs)
STATION_ID  = "my-station-id"
STATION_KEY = "my-station-key"
WU_URL      = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"
ALTITUDE    = 100   # altitude in feet for barometric pressure correction
'''

def sendDataWU(url,statid,statkey,temp,pres,humid,dewpt):
    ''' send sensor data to weather underground '''

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

    ''' build url request string '''
    urlmod = url + "?"
    postdata = urlencode.urlencode(values)
    postdata = postdata.encode('ascii')
    req = requests.post(urlmod, data=postdata)

    ''' uncomment for debugging '''
    #print("Server status code: ", req.status_code, "\n")
    #print(req.headers)
    #print(req.encoding)
    #print(req.text)
    #print(req.json())

def c_to_f(input_temp):
    ''' convert Celsius to Farenheit '''
    return (input_temp * 1.8) + 32

def pa_to_in(input_pressure):
    ''' convert Pa to Inches Hg '''
    return (input_pressure * 0.0295300)

def altitude_cor(input_pressure, alt):
    ''' altitude correction factor for pressure measurement '''
    alt_cor = (760 - alt * 0.026) / 760
    return (input_pressure/alt_cor)

def main():

    '''
    TODO check for valid configuration file
    TODO add ntptime for data logging
    '''

    PORT          = int(cfg["station"]["port"])
    ADDRESS       = int(cfg["station"]["address"],16)
    INTERVAL      = int(cfg["station"]["interval"])
    STATION_ID    = cfg["station"]["station_id"]
    STATION_KEY   = cfg["station"]["station_key"]
    WU_URL        = cfg["station"]["wu_url"]
    ALTITUDE      = int(cfg["station"]["altitude"])

    ''' hardware setup '''
    i2c = I2C(PORT, sda = Pin(0), scl = Pin(1), freq = 400000)
    led = Pin('LED', Pin.OUT)
    wlanc (cfg["wlan"]["ssid"], cfg["wlan"]["pswd"])

    try:
        while True:
            ''' retrieve sensor data '''
            sensor = bme280.BME280(i2c=i2c, address=ADDRESS)
            data = sensor.read_compensated_data()
            temp_raw = data[0]
            pres_raw = data[1]
            humid_raw = data[2]
            dewpoint_raw = sensor.dew_point

            ''' apply conversions '''
            dewpoint_f = round(c_to_f(dewpoint_raw), 3)
            temp_f = round(c_to_f(temp_raw), 3)
            pres_in = pa_to_in(pres_raw/100)
            pres_in_cor = round(altitude_cor(pres_in, ALTITUDE), 3)
            humid = round(humid_raw, 3)

            '''  uncomment for debugging '''
            #print("Temp = ",temp_f)
            #print("Pres = ",pres_in_cor)
            #print("Humi = ",humid)
            #print("Dewp = ",dewpoint_f,"\n")

            ''' send data to weather underground '''
            sendDataWU(WU_URL,STATION_ID,STATION_KEY,temp_f,pres_in_cor,humid,dewpoint_f)

            ''' wait for next reading '''
            for i in range(INTERVAL):
                led.on()
                sleep(.5)
                led.off()
                sleep(.5)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt, exiting")
        led.off()
        sys.exit(0)

    except MemoryError:
        print("\nMemory error, exiting")
        sys.exit(1)

    except OSError as error:
        print("\nOS error, exiting")
        print(error)
        sys.exit(1)

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt, exiting")
        led.off()
        sys.exit(0)
