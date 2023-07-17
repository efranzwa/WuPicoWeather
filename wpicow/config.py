""" config.py

configuration variables for
wlan credentials
weather station configuration
"""

cfg = {
    "wlan": {
        "ssid" : "my-wifi-ssid",
        "pswd" : "my-wifi-password"
    },
    "station": {
        "header": "wpicow",
        "port": "0",
        "address": "119",
        "interval": "300",
        "station_id": "my-station-id",
        "station_key": "my-station-key",
        "wu_url": "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php",
        "altitude": "100"
    }
}
