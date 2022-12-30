#code used to blink the led when button is pressed and send temp reading
#from dhl11 sensor to the aws iot module using mqtt

#version 0.3
#this version uses gpio library to listen for button presses and callbacks to save some resources

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
    GPIO.add_event_detect(37, GPIO.RISING, callback=main, bouncetime=200) #add event, this listens for button presses

def main(channel):

    os.system("sudo insmod piio.ko") #turn LED on
    humidity, temperature = Adafruit_DHT.read(Adafruit_DHT.DHT11, 17) #take the reading form the sensor
    if humidity is not None and temperature is not None: #check if its not empty
        #send the sensor reading to aws using MQTT_publish.py
        os.system("python3 MQTT_publish.py --endpoint a5ta3504qdjkh-ats.iot.eu-central-1.amazonaws.com --ca_file ~/certs/root-CA.crt --cert ~/certs/raspberry_pi_test.cert.pem --key ~/certs/raspberry_pi_test.private.key --client_id basicPubSub --sensor_reading {0:0.1f}".format(temperature))
    else:#reading failed, do not update
        print("Sensor Error");
    os.system("sudo rmmod piio.ko") #turn the LED off

def destroy(): #clean up
    GPIO.cleanup() 
    os.system("sudo rmmod piio.ko")         

if __name__ == '__main__':
    setup()
    try:
        while 1:
            sleep(30)

    except KeyboardInterrupt:
        print("Program closed by user")

    finally:
        destroy()
