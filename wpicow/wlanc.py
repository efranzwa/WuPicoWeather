import network
from time import sleep

def wlanc (ssid, pswd):

    print('starting wifi')

    ssid = ssid
    pswd = pswd

    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected()==True:
        print('connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] + '\n')
        return
    wlan.active(True)
    wlan.connect(ssid, pswd)

    # Wait for connect or fail
    max_wait = 10
    print('waiting for connection.', end='')
    while max_wait > 0:
        if wlan.status() < -5 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('.', end='')
        sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] + '\n')

if __name__=="__main__":
    from config import cfg
    wlanc (cfg["wlan"]["ssid"], cfg["wlan"]["pswd"])
