#This code is used to take the reading from the dht11 sensor and pass it to the MQTT_publish.py.
#While this is happening the LED will turn on and when the reading is sucesfully send then the LED will turn off.

import os
import Adafruit_DHT
import time

try:
     #loop forever. its a quick fix, i wanted it to take a reading when a button was pressed.
     #However, i cannot get python script to execute from the LKM. If have time get button working
    while True:
     os.system("sudo insmod piio.ko") #turn LED on
     humidity, temperature = Adafruit_DHT.read(Adafruit_DHT.DHT11, 17) #take the reading form the sensor
     if humidity is not None and temperature is not None: #check if its not empty
          #send the sensor reading to aws using MQTT_publish.py
          os.system("python3 MQTT_publish.py --endpoint a5ta3504qdjkh-ats.iot.eu-central-1.amazonaws.com --ca_file ~/certs/root-CA.crt --cert ~/certs/raspberry_pi_test.cert.pem --key ~/certs/raspberry_pi_test.private.key --client_id basicPubSub --sensor_reading {0:0.1f}".format(temperature))
          os.system("sudo rmmod piio.ko") #turn the LED off
     else:#reading failed, do not update
          print("Sensor Error");

     time.sleep(5); #delay

except KeyboardInterrupt: #when closing the program with ctr+c remove the lkm again just in case
    os.system("sudo rmmod piio.ko")