from machine import Pin
from time import sleep
##set up input pin
BUTR = Pin(25, Pin.IN)
BUTG = Pin(4, Pin.IN)
##set up output pin
OUTR = Pin(27, Pin.OUT)
OUTG = Pin(12, Pin.OUT)
## counter for red buttom
#  counter for green buttom
counterR = 0
counterG = 0
## always checking
while True:
    # Red buttom was clicked
    if BUTR.value() and not BUTG.value():
        while BUTR.value() and not BUTG.value():
            OUTR.value(1)
            sleep(0.1)
        counterR = counterR +1
            #print(OUTR.value())
        print(counterR)
    # Green tuttom was clicked
    if BUTG.value() and not BUTR.value():
        while BUTG.value() and not BUTR.value():
            OUTG.value(1)
            sleep(0.1)
        counterG = counterG +1
            #print(OUTG.value())
        print(counterG)
    # both not clicked
    if not BUTG.value() and not BUTR.value():
        while not BUTR.value() and not BUTG.value():
            OUTR.value(0)
            OUTG.value(0)
            #sleep(0.1)
    # both clicked
    if BUTR.value() and BUTG.value():
        while BUTR.value() and BUTG.value():
            OUTR.value(0)
            OUTG.value(0)
            sleep(0.1)
        counterR = counterR +1
        counterG = counterG +1
        print(counterR)
        print(counterG)
    # when press any bottom more then 10 times
    if counterR > 8 or counterG > 8:
        if counterR > 8:
            while True:
                OUTR.value(1)
                OUTG.value(0)
                sleep(0.1)
                OUTR.value(0)
                OUTG.value(1)
                sleep(0.1)
                if BUTG.value():
                    print('You have successfully implemented LAB1DEMO!!!' )
                    OUTR.value(0)
                    OUTG.value(0)
                    break
            break
        if counterG > 8:
            while True:
                OUTR.value(1)
                OUTG.value(0)
                sleep(0.1)
                OUTR.value(0)
                OUTG.value(1)
                sleep(0.1)
              
                
                if BUTR.value():
                    print('You have successfully implemented LAB1DEMO!!!' )
                    OUTR.value(0)
                    OUTG.value(0)
                    break
            break