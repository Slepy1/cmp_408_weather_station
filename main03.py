#code used to blink the led when button is pressed and send temp reading
#from dhl11 sensor to the aws iot module using mqtt

#version 1.2
#replaced the piio.c file and added code to start ioctl from python

import RPi.GPIO as GPIO
from time import sleep 
import os
import Adafruit_DHT
from fcntl import ioctl
import ctypes

data = bytes("hello", 'ascii')
dev = os.open("/dev/piiodev", os.O_RDWR)

class gpio_pin(ctypes.Structure): #this holds params to be passed to the driver
    _fields_ = [
        ('descritpion', ctypes.c_ubyte * 16),
        ('pin', ctypes.c_uint),
        ('state', ctypes.c_int),
        ('opt', ctypes.c_char)
    ]

text = "test" #turn string into c char array
text_byte_array = bytearray(text, 'utf-8')
description = (ctypes.c_ubyte * 16)()
description[:len(text_byte_array)] = text_byte_array

Args = gpio_pin()
Args.descritpion = description
Args.pin = 23
Args.state = 0
Args.opt = 0x00

IOCTL_PIIO_GPIO_WRITE = 0x68

def setup():
    GPIO.setmode(GPIO.BOARD) #use physical pin numbers
    GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #setup button
    GPIO.add_event_detect(37, GPIO.RISING, callback=main, bouncetime=200) #add event, this listens for button presses

def main(channel):
    Args.state = 1 #turn LED on
    ioctl(dev,IOCTL_PIIO_GPIO_WRITE,Args)

    humidity, temperature = Adafruit_DHT.read(Adafruit_DHT.DHT11, 17) #take the reading form the sensor
    if humidity is not None and temperature is not None: #check if its not empty
        #send the sensor reading to aws using MQTT_publish.py
        os.system("python3 MQTT_publish.py --endpoint a5ta3504qdjkh-ats.iot.eu-central-1.amazonaws.com --ca_file ~/certs/root-CA.crt --cert ~/certs/raspberry_pi_test.cert.pem --key ~/certs/raspberry_pi_test.private.key --client_id basicPubSub --sensor_reading {0:0.1f}".format(temperature))
    else:#reading failed, do not update
        print("Sensor Error")
    Args.state = 0 #turn the LED off
    ioctl(dev,IOCTL_PIIO_GPIO_WRITE,Args)

def destroy(): #clean up
    Args.state = 0
    ioctl(dev,IOCTL_PIIO_GPIO_WRITE,Args)
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
