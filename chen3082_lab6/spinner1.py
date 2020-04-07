import micropython
from crypt import *
import network
from machine import Timer
from machine import Pin
import machine
from machine import I2C
from machine import PWM
import upip
import ubinascii
from umqtt.simple import MQTTClient
import time
import urequests

def sendMQTT(nodeid,sessionID,x,y,z,t):
    url = "https://maker.ifttt.com/trigger/N*****/with/key/dkrShY0cz-0FUhJ3gD6ySn"
    lib = { "value1" : nodeid+ '|||'+sessionID+ '|||'+ x+'|||' +y+'|||'+z+'|||'+t }

    r = urequests.request("POST", url,\
                      json=lib, headers={"Content-Type": "application/json"})
#### hard code HMAC
# 192.168.43.145
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
# upip.install('micropython-umqtt.robust')
# upip.install('micropython-umqtt.simple')
#upip.install('hmac')
## setting
OUTR = Pin(27, Pin.OUT)
OUTG = Pin(12, Pin.OUT)
OUTY = Pin(33, Pin.OUT)
LED = Pin(13,Pin.OUT)
##switch
BUT1 = Pin(32, Pin.IN)
BUT2 = Pin(14, Pin.IN)

xspeed = 0
yspeed = 0
zspeed = 0

last_value =0
#192.168.43.145
last_value2 = 0
##initI2C
#sessionID = b'1234567890'

CLIENT_ID = ubinascii.hexlify(machine.unique_id())

def sub_cb(topic, msg):
    global sessionID
    print((topic, msg))
    if topic==b'sessionID':
        print(msg)
        sessionID = msg
    elif topic==b"Acknowledge":
        print(msg)
        Ackn = str(msg)



c = MQTTClient(client_id = CLIENT_ID, server = 'm15.cloudmqtt.com',user='ayagnerp', password='j6gUon9xru9w',port ='16060')
c.set_callback(sub_cb)
c.connect()
c.subscribe(b"sessionID")
c.subscribe(b"Acknowledge")


def initI2C():
    global i2c
    global addr
    i2c = I2C(0, scl=Pin(22), sda=Pin(23), freq=400000)
    addr = i2c.scan()              
    print(addr)
initI2C()
##detect press
interruptCounter = 0
interruptCounter2 = 0
def callback(pin):
    global interruptCounter
    interruptCounter += 1
    print('hello')
    LED.value(1)    
    initI2C()
    initaccel()
    clibrate2()
    initTemp()
   
BUT1.irq(trigger=Pin.IRQ_FALLING|Pin.IRQ_RISING, handler = callback)

def callback2(pin):
    global interruptCounter2
    interruptCounter2 += 1

BUT2.irq(trigger=Pin.IRQ_FALLING|Pin.IRQ_RISING, handler = callback2)


def initaccel():
    Format = i2c.readfrom_mem(addr[1],0x31,1)# this is accelerometer
    i2c.writeto_mem(addr[1],0x31,b'\x08')
##  ODR = 800hz 0x2c 1101
    i2c.writeto_mem(addr[1],0x2C,b'\b00001101')
    print("Initialized acceleromater!!!!")
    #measure mode
    i2c.writeto_mem(addr[1],0x2D,b'\b00001000')
    meas = i2c.readfrom_mem(addr[1],0x2D,1)

def hextoLBS(data):
    value = data[1]<<8 | data[0]
#     ## convert to binary
    binvalue = "{0:016b}".format(value)
    binarray = ""
    binvalue = binvalue[6:17]
    if binvalue[0] == '0':
        binarray = binvalue
        x = 9
        intvalue = 0
        for i in binvalue:
            if i =='1':
                intvalue += 2**x
            x = x - 1
    else:
        x = 9
        intvalue = 0
        for i in binvalue:
            if  i =='0':
                binarray += "1"
            elif i =='1':
                binarray += '0'
        for i in binarray:
            if i == '1':
                intvalue += 2**x
            x = x - 1
        intvalue = -(intvalue) - 1
    return intvalue

def calibrate():
    aver1 = 0
    aver2 = 0
    aver3 = 0
    #### read from data register
    for i in range(0,10):
        LSB = i2c.readfrom_mem(addr[1],0x32,6)
        temp1 = LSB[0:2]
        temp1 = hextoLBS(temp1)
        temp2 = LSB[2:4]
        temp2 = hextoLBS(temp2)
        temp3 = LSB[4:6]
        temp3 = hextoLBS(temp3)
        aver1 += temp1
        aver2 += temp2
        aver3 += temp3
    off1 = round(-(aver1/800)/4)
    off2 = round(-(aver2/800)/4)
    off3 = round(-(aver3/800)/4)
   
    return [off1,off2,off3]
def clibrate2():
# #### wipe out the offset register then calibrate
    i2c.writeto_mem(addr[1],0x1E,b'\x00')
    i2c.writeto_mem(addr[1],0x1F,b'\x00')
    i2c.writeto_mem(addr[1],0x20,b'\x00')
    x , y, z = calibrate()
# ####write to offset
    i2c.writeto_mem(addr[1],0x1E,bytearray([x]))
    i2c.writeto_mem(addr[1],0x1F,bytearray([y]))
    i2c.writeto_mem(addr[1],0x20,bytearray([z]))
    print("calibrated acceleromater!!!!")

def getacc():
    LSB = i2c.readfrom_mem(addr[1],0x32,6)
    temp1 = LSB[0:2]
    temp1 = hextoLBS(temp1)
    xacc = ((temp1/256)*9.8)
    temp2 = LSB[2:4]
    temp2 = hextoLBS(temp2)
    yacc = ((temp2/256)*9.8)
    temp3 = LSB[4:6]
    temp3 = hextoLBS(temp3)
    zacc = (((temp3/256)+1)*9.8)
    return (xacc, yacc, zacc)
gx = 0
gy = 0
gz = 0

# #### initialize temperature
def initTemp():
    global temp
    i2c.writeto_mem(addr[0],0x03,b'\x01')
    test = i2c.readfrom_mem(addr[0],0x03,1)
    print("Initialized temperature Sensor")

counter = 0
#
while 1:
 
    if interruptCounter:
        state = machine.disable_irq()
        interruptCounter = interruptCounter - 1
        machine.enable_irq(state)
#
    if interruptCounter2:
        state = machine.disable_irq()
        interruptCounter2 = interruptCounter2 - 1
        machine.enable_irq(state)
        #### getacc() for acc, value1 for temp
        ## temp is the first temp
        print('test')
        #pwmG = PWM(Pin(13),freq=10,duty=512)
        ### sub to sessionID
#         subs()
#         print("sessionID",sessionID)
#         print('done')
        while 1:
            
            c.wait_msg()
            print("sessionID",sessionID)
            ## detect measurement
            data = i2c.readfrom_mem(addr[0],0x00,2)
            value1 = data[0]<<8 | data[1]
            value1 = value1/128  #### this is temp
            acc = getacc()
            print(acc)
            print(value1)
            #sensorData = [round(acc[0]),round(-1),round(acc[2]),round(value1)]
            
            #### encrypt with hardcode the IV
            print("sessionID",sessionID)
            a = ''
            for i in range(16):
                a += chr(random.randint(97,122))
            data = CryptAes(CLIENT_ID,a,sessionID)
           
            sendMQTT(CLIENT_ID,sessionID,str(acc[0]),str(acc[1]),str(acc[2]),str(value1))
            SensorData = str(acc[0])+' '+ str(acc[1])+ ' '+str(acc[2])+' '+str(value1)
            SensorData = data.encrypt(SensorData)
            
            HMAC  =data.sign_hmac(sessionID)
            #print('HMAC',HMAC)
            JSON = data.send_mqtt(HMAC)
            #print(JSON)
            c.publish(b"Sensor_Data",JSON)
            c.wait_msg()
            #print('really?')
            ####hardcode sessioonID makeHMAC
           
#             ## sub to Acknowledge
#             #subsA()
#            
#             HMAC=data.sign_hmac(data.enData+data.nodeid+data.iv+sessionID)
#             HMAC=data.send_mqtt(HMAC)