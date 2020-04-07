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
upip.install('micropython-umqtt.robust')
upip.install('micropython-umqtt.simple')
upip.install('hmac')
## setting
OUTR = Pin(27, Pin.OUT)
OUTG = Pin(12, Pin.OUT)
OUTY = Pin(33, Pin.OUT)
LED = Pin(13,Pin.OUT)
##switch
BUT1 = Pin(4, Pin.IN)
BUT2 = Pin(36, Pin.IN)


##initI2C

def publishA(content):
    c = MQTTClient(client_id = CLIENT_ID, server='m15.cloudmqtt.com',user='ayagnerp', password='j6gUon9xru9w',port ='16060')
    c.connect()
    c.publish(b"Acknowledge",content)
    c.disconnect()
    
def publishSessionID(content):
    c = MQTTClient(client_id = CLIENT_ID, server='m15.cloudmqtt.com',user='ayagnerp', password='j6gUon9xru9w',port ='16060')
    c.connect()
    c.publish(b"sessionID",content)
    c.disconnect()
    
def sub_cb(topic, msg):
    global sessionID,Sensor_Data
    print((topic, msg))
    if topic==b'Sensor_Data':
        Sensor_Data = msg
        

def subs(server="m15.cloudmqtt.com"):
    global client_id, mqtt_server, topic_sub

    c = MQTTClient(client_id = CLIENT_ID, server = 'm15.cloudmqtt.com',user='ayagnerp', password='j6gUon9xru9w',port ='16060')
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(b"Sensor_Data")
    c.wait_msg()
    c.disconnect()
####publish message on the sessionID every one second
tim = Timer(0)
sessionID=''
counter =0
def handleInterrupt(tim):
    global sessionID
    global counter
    temp = bytes([random.getrandbits(5)])
    publishSessionID(temp)
    
    if counter ==0:
        sessionID = temp
        counter+=1
        print(sessionID)
        
tim.init(period=(1*1000), mode= Timer.PERIODIC, callback=handleInterrupt)


####generate HMAC
####check if HMAC the same
####decrypt
# enData = b'g\r\xcd\x90\xba\xc1\x84`p\xe5Y\xb1\xd5\x07w\xd8mmM\xa5L\xb0\xb8\x1a}<\xa7\xb4\x81>\x90\xa6cJ$\xa8\x85\x85\xbf\xe0B\x86Ef\xe8\x8f\xb5P'
#     #### how to initialize class
# SensorData=enData[:16]
# nodeid = enData[16:32]
# iv = enData[32:48]

#sessionID = bytes(random.getrandbits(10))

# data = CryptAes(nodeid,iv,sessionID)
# Data = data.decrypt(SensorData)
# print('data',Data[0])
# print('data',Data[1])
# print('data',Data[2])
# print('data',Data[3])
# xaccl = Data[0]
# yaccl = Data[1]
# zaccl = Data[2]
# temp  = Data[3]

def initI2C():
    global i2c
    global addr
    i2c = I2C(0, scl=Pin(22), sda=Pin(23), freq=400000)
    addr = i2c.scan()              # scan for slave devices
    print(addr)


##detect press
interruptCounter = 0
interruptCounter2 = 0
def callback(pin):
    global interruptCounter
    interruptCounter += 1
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
    i2c.writeto_mem(addr[1],0x2C,b'\b00001101')
    print("Initialized acceleromater!!!!")
    #measure mode
    i2c.writeto_mem(addr[1],0x2D,b'\b00001000')
    meas = i2c.readfrom_mem(addr[1],0x2D,1)

### convert hex to integer
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
    #### read from temp data register
    for i in range(0,800):
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
# #### wipe out the offset register
    i2c.writeto_mem(addr[1],0x1E,b'\x00')
    i2c.writeto_mem(addr[1],0x1F,b'\x00')
    i2c.writeto_mem(addr[1],0x20,b'\x00')
    ## do the calibrate()
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
    #### store temperature in temp
    data = i2c.readfrom_mem(addr[0],0x00,2)
    value = data[0]<<8 | data[1]
    value = value/128
    temp = value

counter = 0
while 1:
 
    if interruptCounter:
        state = machine.disable_irq()
        interruptCounter = interruptCounter - 1
        machine.enable_irq(state)
    if interruptCounter2:
        state = machine.disable_irq()
        interruptCounter2 = interruptCounter2 - 1
        machine.enable_irq(state)
        print('test')
        pwmG = PWM(Pin(13),freq=10,duty=512)
        
        while 1:
            ####sub to Sensor
            subs()
            print(Sensor_msg)
            
            ####publish on Anckowlegement
            #publishA()
            #counter +=1    
            #if counter == 20:
            #    print("accl:", getacc())
            #    print("temp:",value1)
            #    counter = 0
            ## detect measurement
            
            
#             if (abs(value1-temp)>1) :
#                 pwmG = PWM(Pin(13),freq=10 +5*round(value1-temp),duty=512)

    