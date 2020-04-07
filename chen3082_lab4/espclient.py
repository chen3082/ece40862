from machine import Pin
import network
import esp32
from machine import Timer
import usocket
import socket
import urequests

Red = Pin(12,Pin.OUT,Pin.PULL_UP)
OUTR = Pin(13, Pin.OUT)

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('youarenot', 'mytrigger')
        while not wlan.isconnected():
            pass
    print('Oh YES! Get connected')
    print('Connected to nope')
    #print('MAC Address: ', transfer(wlan.config('mac')))
    print('network config:', wlan.ifconfig()[0])
    
do_connect()
tim = Timer(0)
print(esp32.hall_sensor())
print(esp32.raw_temperature())
counter = 0
addr = usocket.getaddrinfo('www.thingspeak.com',80)[0][-1]
#mysocket = getSocket(type="TCP")
#print('heelo'+ str(addr))
#s = usocket.socket()
#s.connect(addr)
#data = "field1="+str(esp32.hall_sensor())+"&field2="+str(esp32.raw_temperature())
#response = urequests.get('https://api.thingspeak.com/update?api_key=YO282TSJI25DUDBU&'+data)
s = usocket.socket()
def handleInterrupt(tim):
    global addr
    print(esp32.raw_temperature())
    print(esp32.hall_sensor())
    s = usocket.socket()
    s.connect(addr)
    addr = usocket.getaddrinfo('www.thingspeak.com',80)[0][-1]
    #s = usocket.socket()
    imfor = "field1="+str(esp32.raw_temperature())+"&field2="+str(esp32.hall_sensor())
    s.send(b'GET https://api.thingspeak.com/update?api_key=YO282TSJI25DUDBU&{} HTTP/1.0\r\n\r\n'.format(imfor))
    s.close()
    #response = urequests.get('https://api.thingspeak.com/update?api_key=YO282TSJI25DUDBU&'+data)
    #response.close()
tim.init(period=(10*1000), mode= Timer.PERIODIC, callback=handleInterrupt)




upip.install('micropython-umqtt.simple')
upip.install('micropython-umqtt.robust')
upip.install('micropython-hmac')






