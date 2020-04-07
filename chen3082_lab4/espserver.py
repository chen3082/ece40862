from machine import Pin
import network
import esp32
from machine import Timer
import usocket
import socket
import urequests
# reference from 
# Global variables
Red = Pin(12,Pin.OUT,Pin.PULL_UP)
Green = Pin(13, Pin.OUT)
temp=esp32.raw_temperature()  # measure temperature sensor data
hall=str(esp32.hall_sensor())  # measure hall sensor data
red_led_state="on" # string, check state of red led, ON or OFF
green_led_state="off" # string, check state of red led, ON or OFF
#led=Pin(12,Pin.OUT,Pin.PULL_UP)

def web_page():
    
        
    """Function to build the HTML webpage which should be displayed
    in client (web browser on PC or phone) when the client sends a request
    the ESP32 server.
    
    The server should send necessary header information to the client
    (YOU HAVE TO FIND OUT WHAT HEADER YOUR SERVER NEEDS TO SEND)
    and then only send the HTML webpage to the client.
    
    Global variables:
    TEMP, HALL, RED_LED_STATE, GREEN_LED_STAT
    """
    
    html_webpage = """<!DOCTYPE HTML><html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
    <style>
    html {
     font-family: Arial;
     display: inline-block;
     margin: 0px auto;
     text-align: center;
    }
    h2 { font-size: 3.0rem; }
    p { font-size: 3.0rem; }
    .units { font-size: 1.5rem; }
    .sensor-labels{
      font-size: 1.5rem;
      vertical-align:middle;
      padding-bottom: 15px;
    }
    .button {
        display: inline-block; background-color: #e7bd3b; border: none; 
        border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none;
        font-size: 30px; margin: 2px; cursor: pointer;
    }
    .button2 {
        background-color: #4286f4;
    }
    </style>
    </head>
    <body>
    <h2>ESP32 WEB Server</h2>
    <p>
    <i class="fas fa-thermometer-half" style="color:#059e8a;"></i> 
    <span class="sensor-labels">Temperature</span> 
    <span>"""+str(temp)+"""</span>
    <sup class="units">&deg;F</sup>
    </p>
    <p>
    <i class="fas fa-bolt" style="color:#00add6;"></i>
    <span class="sensor-labels">Hall</span>
    <span>"""+str(hall)+"""</span>
    <sup class="units">V</sup>
    </p>
    <p>
    RED LED Current State: <strong>""" + red_led_state + """</strong>
    </p>
    <p>
    <a href="/?red_led=on"><button class="button">RED ON</button></a>
    </p>
    <p><a href="/?red_led=off"><button class="button button2">RED OFF</button></a>
    </p>
    <p>
    GREEN LED Current State: <strong>""" + green_led_state + """</strong>
    </p>
    <p>
    <a href="/?green_led=on"><button class="button">GREEN ON</button></a>
    </p>
    <p><a href="/?green_led=off"><button class="button button2">GREEN OFF</button></a>
    </p>
    </body>
    </html>"""
    return html_webpage

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

# def web_page():
#   if led.value() == 1:
#     gpio_state="ON"
#   else:
#     gpio_state="OFF"
#   
#   html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
#   <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
#   h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
#   border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
#   .button2{background-color: #4286f4;}</style></head><body> <h1>ESP Web Server</h1> 
#   <p>GPIO state: <strong>""" + gpio_state + """</strong></p><p><a href="/?led=on"><button class="button">ON</button></a></p>
#   <p><a href="/?led=off"><button class="button button2">OFF</button></a></p></body></html>"""
#   return html

do_connect()

#set up client
#send header
#create server using socket API to listen request
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
  conn, addr = s.accept()
  print('Got a connection from %s' % str(addr))
  request = conn.recv(1024)
  request = str(request)
  print('Content = %s' % request)
  led_on = request.find('/?red_led=on')
  led_off = request.find('/?red_led=off')
  if led_on == 6:
    print('LED ON')
    Red.value(1)
    red_led_state="ON"
  if led_off == 6:
    print('LED OFF')
    Red.value(0)
    red_led_state="off"
  led_on2 = request.find('/?green_led=on')
  led_off2 = request.find('/?green_led=off')
  if led_on2 == 6:
    #print('LED ON')
    Green.value(1)
    green_led_state="on"
  if led_off2 == 6:
    #print('LED OFF')
    Green.value(0)
    green_led_state="off"
  response = web_page()
  conn.send('HTTP/1.1 200 OK\n')
  conn.send('Content-Type: text/html\n')
  conn.send('Connection: close\n\n')
  conn.sendall(response)
  conn.close()
