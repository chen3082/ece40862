from machine import Pin
from machine import PWM
from machine import Timer
from machine import RTC
from machine import ADC
import machine
from time import sleep
from utime import ticks_ms
#
Year=int(input('year?'))
Month=int(input('Month?'))
Day=int(input('Day?'))
Weekday=int(input('Weekday?'))
Hour=int(input('hour?'))
Minute=int(input('Minute?'))
Second=int(input('second?'))
Microsecond=int(input('Microsecond?'))

OUTR = Pin(27, Pin.OUT)
flag = 0
###  timer interrupt1
interruptCounter = 0

def handleInterrupt(tim):
    (year,month,day,foo1,hour,minute,second,foo2) =rtc.datetime()
    print("Date: {:02d}.{:02d}.{}\nTime: {:02d}:{:02d}:{:02d}".format(month,day,year,hour,minute,second))



tim.init(period=(30*1000), mode= Timer.PERIODIC, callback=handleInterrupt)

#set up real time clock
rtc = RTC()
rtc.init((Year,Month,Day,Weekday,Hour,Minute,Second,Microsecond))
(year,month,day,foo1,hour,minute,second,foo2) =rtc.datetime()
print(rtc.datetime())
print("Date: {:02d}.{:02d}.{}\nTime: {:02d}:{:02d}:{:02d}".format(month,day,year,hour,minute,second))

#set up adc
adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)
adc.width(ADC.WIDTH_9BIT)


counter = 0
#interruptCounter2
interruptCounter2 = 0
tim2 = Timer(-1)
flag=0

def handleInterrupt2(tim2):

    if counter>0 and (counter-1)%2==0:
        pwmR.deinit()
        #counterR +=1
        ledR=Pin(13,Pin.OUT)

        tim4=Timer(1)
        def handleInterrupt4(tim4):
            global flag
            if flag%2==0:
                ledR.value(1)
                flag+=1
            else:
                flag+=1
                ledR.value(0)
        #print(adc.read())
        tim4.init(freq=(adc.read()+1), mode= Timer.PERIODIC, callback = handleInterrupt4)


    if counter>0 and counter%2==0:
        pwmG = PWM(Pin(12),freq=10,duty=adc.read())



tim2.init(period=(100), mode= Timer.PERIODIC, callback=handleInterrupt2)

##pwm
pwmR = PWM(Pin(13),freq=10,duty=256)
pwmG = PWM(Pin(12),freq=10,duty=256)
##switch
BUT = Pin(4, Pin.IN)

last_value =0
def callback(pin):
#     fir = BUT.value()
#     if BUT.value==1:
#         fir = BUT.value()
#     elif fir!=BUT.value() and not BUT.value():
    global last_value
    global counter
    value=0
    #print(ticks_ms())
    diff = ticks_ms()-last_value
    #print(int(diff))
    if int(diff)>500:
        counter +=1
        #print('interrupt has occured',counter)
        last_value = ticks_ms()


BUT.irq(trigger=Pin.IRQ_FALLING|Pin.IRQ_RISING, handler = callback)
