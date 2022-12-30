#code used to blink the led when button is pressed and send temp reading
#from dhl11 sensor to the aws iot module using mqtt

#version 0.3
#this version uses gpio library to listen for button presses and threads

#todo
#the code is working
#if have time try to replace gpio library with your own lkm 

#notes for future debugging
#1. connect button to 3.3v not to gnd. 2.dont use that oled screen, its broken. 3. 10k omh resistor is too high.

import RPi.GPIO as GPIO
from time import sleep 
import os
import Adafruit_DHT

def setup():
    GPIO.setmode(GPIO.BOARD) #use physical pin numbers
    GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #setup button
    GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW) #setup led

def motorcontrol():
    while True:
        sleep(0.1)
        button=GPIO.input(37)
        if button==1: #Robot is activated when button is pressed
            print ("start ")

            GPIO.output(16, GPIO.HIGH) # Turn on

            humidity, temperature = Adafruit_DHT.read(Adafruit_DHT.DHT11, 17) #take the reading form the sensor
            if humidity is not None and temperature is not None: #check if its not empty
                #send the sensor reading to aws using MQTT_publish.py
                os.system("python3 MQTT_publish.py --endpoint a5ta3504qdjkh-ats.iot.eu-central-1.amazonaws.com --ca_file ~/certs/root-CA.crt --cert ~/certs/raspberry_pi_test.cert.pem --key ~/certs/raspberry_pi_test.private.key --client_id basicPubSub --sensor_reading {0:0.1f}".format(temperature))
            else:#reading failed, do not update
                print("Sensor Error");
            GPIO.output(16, GPIO.LOW)  # Turn off

def destroy():
    GPIO.cleanup()                     # Release resource               

if __name__ == '__main__':     # Program start from here
    setup()
    try:
        motorcontrol()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
