import network
from machine import Timer
from machine import Pin
import machine
from machine import I2C
from machine import PWM
import upip
import ubinascii
from umqtt.simple import MQTTClient
from crypt import *
import time
import urequests
import random

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('youarenot', 'mytrigger')
        #wlan.connect('Yunlei的iPhone','xxbbt123')
        #wlan.connect("Heiren","12345678")
        while not wlan.isconnected():
            pass
    print('Oh YES! Get connected')
    print('Connected to nope')
    #print('MAC Address: ', transfer(wlan.config('mac')))
    print('network config:', wlan.ifconfig()[0])
do_connect()
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
#upip.install('micropython-umqtt.robust')
#upip.install('micropython-umqtt.simple')
#upip.install('hmac')
## setting
OUTR = Pin(27, Pin.OUT)
#OUTG = Pin(12, Pin.OUT)
OUTY = Pin(33, Pin.OUT)
LED = Pin(13,Pin.OUT)
##switch
BUT1 = Pin(4, Pin.IN)
BUT2 = Pin(36, Pin.IN)


def sendMQTT(nodeid,sessionID,x,y,z,t):
    url = "https://maker.ifttt.com/trigger/MOM/with/key/hLKtFm2TIKYMfXYWIAyx5dvgMpHRbTQDG3lCBRDsCOx"
    lib = { "value1" : str(nodeid)+ '|||'+str(sessionID)+ '|||'+ str(x)+'|||' +str(y)+'|||'+str(z)+'|||'+str(t) }

    r = urequests.request("POST", url,\
                      json=lib, headers={"Content-Type": "application/json"})

def sub_cb(topic, msg):
    global sessionID,Sensor_Data,ack
    global temp
    print((topic, msg))
   
    if topic==b'Sensor_Data':
        Sensor_Data = msg

c = MQTTClient(client_id = ubinascii.hexlify(machine.unique_id()), \
               server = 'm15.cloudmqtt.com',user='ayagnerp', password='j6gUon9xru9w',port ='16060')
c.set_callback(sub_cb)
c.connect()
c.subscribe(b"Sensor_Data")

####publish message on the sessionID every one second
tim = Timer(0)
counter =0
ack = 1
temp = 0
temp1 = 0
def handleInterrupt(tim):
    global temp
    global temp1
    global counter
    global ack
    if ack==1:
        #temp1 = temp
        temp = bytes([random.getrandbits(5)])
        
        print("sessionID",temp)
        c.publish(b"sessionID",ubinascii.hexlify(temp))
        #print('where')
#         try:
#             c.publish(b"sessionID",ubinascii.hexlify(temp2))
#         except:
#             pass
        
tim.init(period=(5*1000), mode= Timer.PERIODIC, callback=handleInterrupt)    
value1 = 25
while 1:
    c.wait_msg()
    Sensor_Data = json.loads(Sensor_Data)
    pwmG = PWM(Pin(12),freq=10,duty=512)
    LED.value(1)
    #print("TEMp: ",temp)
    #print("test:",temp)
    spi2 = CryptAes(ubinascii.unhexlify(Sensor_Data["ID"]),ubinascii.unhexlify(Sensor_Data["IV"]),temp)
    Ack = spi2.verify_hmac(Sensor_Data)
    c.publish(b"Acknowledge",Ack)
    if Ack=="Successful Decryption":
        SensorData = spi2.decrypt(Sensor_Data)
        x,y,z,t = str(SensorData).split(' ')
        t = float(t[:8])
        x =x[2:]
        sendMQTT(spi2.nodeid,temp,x,y,z,t)
        print(abs(float(x)*100))
        print(abs(float(y)*100))
        print(float(z)*100)
              
        if (abs(float(x)*100)>100) or (abs(float(y)*100)>100) or ((float(z)*100)>2000):
            OUTR.value(1)
            
        else:
            OUTR.value(0)
        if (abs(value1-t)>1) :
                pwmG = PWM(Pin(12),freq=10 +5*round(value1-t),duty=512)
        value1 = t
       # print(value1)

        
