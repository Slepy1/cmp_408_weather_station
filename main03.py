#code used to blink the led when button is pressed and send temp reading
#from dhl11 sensor to the aws iot module using mqtt

#version 0.3
#this version uses gpio library to listen for button presses and callbacks to save some resources

#version 1
#replaced the piio.c file, now rather than controlling led with command os.system("sudo insmod piio.ko")
#the file /dev/piiodev is opened and led is turned on by os.write(dev,data) and turned off by os.read(dev, test)

#todo
#the code is working
#if have time try improving the piio.c

#notes for future debugging
#1. connect button to 3.3v not to gnd. 2.dont use that oled screen, its broken. 3. 10k omh resistor is too high.

import RPi.GPIO as GPIO
from time import sleep 
import os
import Adafruit_DHT

data = bytes("hello", 'ascii')
dev = os.open("/dev/piiodev", os.O_RDWR)
test = 1

def setup():
    GPIO.setmode(GPIO.BOARD) #use physical pin numbers
    GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #setup button
    GPIO.add_event_detect(37, GPIO.RISING, callback=main, bouncetime=200) #add event, this listens for button presses

def main(channel):
    os.write(dev,data) #turn LED on
    humidity, temperature = Adafruit_DHT.read(Adafruit_DHT.DHT11, 17) #take the reading form the sensor
    if humidity is not None and temperature is not None: #check if its not empty
        #send the sensor reading to aws using MQTT_publish.py
        os.system("python3 MQTT_publish.py --endpoint a5ta3504qdjkh-ats.iot.eu-central-1.amazonaws.com --ca_file ~/certs/root-CA.crt --cert ~/certs/raspberry_pi_test.cert.pem --key ~/certs/raspberry_pi_test.private.key --client_id basicPubSub --sensor_reading {0:0.1f}".format(temperature))
    else:#reading failed, do not update
        print("Sensor Error");
    os.read(dev, test) #turn the LED off

def destroy(): #clean up 
    os.read(dev, test) #turn the LED off
    GPIO.cleanup() 

if __name__ == '__main__':
    setup()
    try:
        while 1:
            sleep(30)

    except KeyboardInterrupt:
        print("Program closed by user")

    finally:
        destroy()
