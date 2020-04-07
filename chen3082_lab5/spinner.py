import network
from machine import Timer
from machine import TouchPad, Pin
import time
import machine
import esp32
import utime
from machine import I2C
from utime import ticks_ms
import binascii
import math
from machine import PWM



OUTR = Pin(27, Pin.OUT)
OUTG = Pin(12, Pin.OUT)
OUTY = Pin(33, Pin.OUT)
LED = Pin(13,Pin.OUT)
##switch
BUT1 = Pin(4, Pin.IN)
BUT2 = Pin(36, Pin.IN)

xspeed = 0
yspeed = 0
zspeed = 0

last_value =0

last_value2 = 0 

def initI2C():
    global i2c
    global addr
    i2c = I2C(0, scl=Pin(22), sda=Pin(23), freq=400000)
    addr = i2c.scan()              # scan for slave devices
    print(addr)
    ID = i2c.readfrom_mem(addr[0],0x0B,1)# this is temperature
    ID2 = i2c.readfrom_mem(addr[1],0x00,1)# this is accelerometer
    if ID!=b"\xcb":
        raise ValueError('wrong id')
    if ID2!=b'\xe5':
        raise ValueError('wrong id')
#while 1:
# check device id
def checkID():
    ID = i2c.readfrom_mem(addr[0],0x0B,1)# this is temperature
    ID2 = i2c.readfrom_mem(addr[1],0x00,1)# this is accelerometer
    if ID!=b"\xcb":
        raise ValueError('wrong id')
    if ID2!=b'\xe5':
        raise ValueError('wrong id')

#i2c.writeto_mem(addr,0x2D,b'00')
#data =i2c.readfrom_mem(addr,,8)
# couldn't convert 

## set data_format 2bit
def initaccel():
    Format = i2c.readfrom_mem(addr[1],0x31,1)# this is accelerometer
    i2c.writeto_mem(addr[1],0x31,b'\x08')
# Format = i2c.readfrom_mem(addr[1],0x31,1)# this is accelerometer

##  ODR = 800hz 0x2c 1101
    i2c.writeto_mem(addr[1],0x2C,b'\b00001101')
    print("Initialized acceleromater!!!!")
    #measure mode 
    i2c.writeto_mem(addr[1],0x2D,b'\b00001000')
    meas = i2c.readfrom_mem(addr[1],0x2D,1)
## calibrate
# test = i2c.readfrom_mem(addr[1],0x2D,1)



def hextoLBS(data):
    value = data[1]<<8 | data[0]
    ## convert to binary
    binvalue = "{0:016b}".format(value)
    #print("binvalue" + binvalue)

    binarray = ""
    binvalue = binvalue[6:17]
    #print("10bvalue:",binvalue)
    #print((value))
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
        #print(binarray)
        for i in binarray:
            if i == '1':
                intvalue += 2**x
            x = x - 1
        intvalue = -(intvalue) - 1
    #print('binarray:', binarray)
    #print('intvalue:', intvalue)
    return intvalue

## calibrate
def calibrate():
    aver1 = 0
    aver2 = 0
    aver3 = 0
    #### read from data register
    for i in range(0,800):
        LSB = i2c.readfrom_mem(addr[1],0x32,6)
        #print("LSB:",LSB)
        temp1 = LSB[0:2]
        #print("temp1:",temp1)
        temp1 = hextoLBS(temp1)
        #print("temp1",temp1)
        temp2 = LSB[2:4]
        #print("temp2:",temp2)
        temp2 = hextoLBS(temp2)
        #print("temp2:",temp2)
        temp3 = LSB[4:6]
        #print("temp3:",temp3)
        temp3 = hextoLBS(temp3)
        #print("temp3:",temp3)
        aver1 += temp1
        aver2 += temp2
        aver3 += temp3
    off1 = round(-(aver1/800)/4)
    off2 = round(-(aver2/800)/4)
    off3 = round(-(aver3/800)/4)
    
    return [off1,off2,off3]
def clibrate2():
#### wipe out the offset register
    i2c.writeto_mem(addr[1],0x1E,b'\x00')
    i2c.writeto_mem(addr[1],0x1F,b'\x00')
    i2c.writeto_mem(addr[1],0x20,b'\x00')
    #LSB = i2c.readfrom_mem(addr[1],0x1E,3)# this is accelerometer
    x , y, z = calibrate()

#print(x,y,z)
##print("testtest",bytearray([x]),bytearray([y]),bytearray([z]))

####write to offset
    i2c.writeto_mem(addr[1],0x1E,bytearray([x]))
    i2c.writeto_mem(addr[1],0x1F,bytearray([y]))
    i2c.writeto_mem(addr[1],0x20,bytearray([z]))
    print("calibrated acceleromater!!!!")

#### checking the write is correct Y
#LSB = i2c.readfrom_mem(addr[1],0x1E,3)# this is accelerometer
#print("LLSB:",LSB)


def getacc():
    LSB = i2c.readfrom_mem(addr[1],0x32,6)# this is accelerometer

    temp1 = LSB[0:2]
    temp1 = hextoLBS(temp1)
    xacc = ((temp1/256)*9.8)
    temp2 = LSB[2:4]
    temp2 = hextoLBS(temp2)
    yacc = ((temp2/256)*9.8)
    temp3 = LSB[4:6]
    temp3 = hextoLBS(temp3)
    zacc = (((temp3/256)+1)*9.8)

    return [xacc, yacc, zacc]
gx = 0
gy = 0
gz = 0
#### calculate velocity
def getvel():
    global xspeed
    global yspeed
    global zspeed
    global gx,gy,gz
    xaccl, yaccl, zaccl = getacc()
    xspeed = xspeed + xaccl
    gx = 0.9*gx + 0.1*xspeed
    xspeed -= gx
    yspeed = yspeed + yaccl
    gy = 0.9*gy + 0.1*yspeed
    yspeed -= gy
    zspeed = zspeed + zaccl - 9.8
    gz = 0.9*gz + 0.1*zspeed
    zspeed -= gz
    #### reset the speed if the motion wing stay still
    if (-0.25)<xaccl<0.25:
        xspeed = 0
    if (-0.25)<yaccl<0.25:
        yspeed = 0
    if (-0.25)<zaccl<0.25:
        zspeed = 0
    
        
#### light up the red led       
def lightRed():
    global xspeed
    if (xspeed>5) | (xspeed<-5) | (yspeed>5) | (yspeed<-5) | (zspeed>5):
        OUTR.value(1)
    else:
        OUTR.value(0)
    
#### measure the Angle
#### couldn't get z to work
def getAngle():
    xaccl, yaccl, zaccl = getacc()
    #print("nmsl", xaccl,yaccl,zaccl)
    if ((yaccl*yaccl+zaccl*zaccl)**(1/2)) !=0:
        xangle = math.atan(xaccl/((yaccl*yaccl+zaccl*zaccl)**(1/2)))
    else:
        xangle = 0
    if ((xaccl*xaccl+zaccl*zaccl)**(1/2)) != 0:
        yangle = math.atan(yaccl/((xaccl*xaccl+zaccl*zaccl)**(1/2)))
    else:
        yangle = 0
    if zaccl != 0:
        zangle = math.atan(((xaccl*xaccl+yaccl*yaccl)**(1/2))/zaccl)
    else:
        zangle = 0
    #xangle = math.atan2(xaccl,zaccl)*57.3
    #return xangle
    ### light up yellow or green
    if (abs(xangle*57.3)>30) | (abs(yangle*57.3)>30) | (abs(zangle*57.3)>30):
        OUTY.value(1)
    else: 
        OUTY.value(0)
    if (abs(xangle*57.3)<30) & (abs(yangle*57.3)<30) & (abs(zangle*57.3)<30) & (abs(xspeed)<5) & (abs(yspeed)<5)& abs(zspeed<5):
        OUTG.value(1)
    else:
        OUTG.value(0)
    if (xspeed>5) | (xspeed<-5) | (yspeed>5) | (yspeed<-5) | (zspeed>5):
        OUTR.value(1)
    else:
        OUTR.value(0)
    return [xangle*57.3,yangle*57.3,zangle*57.3]

#### initialize temperature
def initTemp():
    global temp
    i2c.writeto_mem(addr[0],0x03,b'\x01')
    test = i2c.readfrom_mem(addr[0],0x03,1)
    print("Initialized temperature Sensor")
    #### store temperature in temp
    pwmG = PWM(Pin(13),freq=10,duty=512)
    data = i2c.readfrom_mem(addr[0],0x00,2)
    value = data[0]<<8 | data[1]
    value = value/128
    temp = value
     
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
        
            ##BUT1.irq(trigger=Pin.IRQ_FALLING|Pin.IRQ_RISING, handler = callback)

BUT2.irq(trigger=Pin.IRQ_FALLING|Pin.IRQ_RISING, handler = callback2)

counter = 0

while 1:
 
    if interruptCounter:
        state = machine.disable_irq()
        interruptCounter = interruptCounter - 1
        machine.enable_irq(state)
        LED.value(1)    
        initI2C()
        initaccel()
        clibrate2()
        initTemp()
    if interruptCounter2:
        state = machine.disable_irq()
        interruptCounter2 = interruptCounter2 - 1
        machine.enable_irq(state)
        print('test')
        while 1:
            getvel()
            counter +=1    
            if counter == 20:
                print("speed:",xspeed,yspeed,zspeed)
                print("Angle",getAngle())
                print("temp:",value1)
                counter = 0
            ## detect measurement
            data = i2c.readfrom_mem(addr[0],0x00,2)
            value1 = data[0]<<8 | data[1]
            value1 = value1/128
            if (abs(value1-temp)>1) :
                pwmG = PWM(Pin(13),freq=10 +5*round(value1-temp),duty=512)
            temp = value1