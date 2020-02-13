from firebase import firebase  
import time
from datetime import datetime
import random
import sys
import RPi.GPIO as io
from Adafruit_IO import MQTTClient
import requests


ADAFRUIT_IO_KEY      = ''       # adafruit key
ADAFRUIT_IO_USERNAME = ''  		# adafruit username


io.cleanup()
io.setmode(io.BCM)
io.setwarnings(False)


io.setup(18,io.OUT)
io.output(18, io.HIGH)
io.setup(12,io.OUT)
#io.output(12, io.HIGH)

def connected(client):
    print('Connected. Listening changes...')
    client.subscribe('bulb')
    client.subscribe('fan')
    
def disconnected(client):   
    print('Disconnected !')
    sys.exit(1)

def message(client, feed_id, status):
    global st, sd, sday, st1, oncommand
    try:
        if feed_id == 'bulb':
            if status=='1':
                st = datetime.now().strftime('%H:%M:%S')
                sd = datetime.now().strftime('%Y:%m:%d')
                sday = int(datetime.now().strftime('%d'))
                st1 = time.time()
                oncommand = "Bulb ON"
                print("{} : {} {} {} {}".format(oncommand,sd,st,sday,st1))
                io.output(18,io.LOW)
                time.sleep(10)
            else:
                et = datetime.now().strftime('%H:%M:%S')
                ed = datetime.now().strftime('%Y:%m:%d')
                eday = int(datetime.now().strftime('%d'))
                et1 = time.time()
                offcommand = "Bulb OFF"
                timediff = et1 - st1
                print("{} : {} {} {} {}".format(offcommand,ed,et,eday,et1))
                print(timediff)
                from firebase import firebase

                firebase = firebase.FirebaseApplication('https://database.firebaseio.com/', None)  # firebase db link

                data =  { 'start_date': sd,
                          'start_time': st,
                          'end_date': ed,
                          'end_time': et,
                          'timediff': timediff,
                        }  
                result = firebase.post('/table_name/',data)  # db -> table_name
                print(result)
                
                io.output(18,io.HIGH)
                
                     
    except KeyboardInterrupt:
        io.output(12,io.HIGH)
        io.output(18,io.HIGH)
    
        
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)


client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message


client.connect()


client.loop_blocking()