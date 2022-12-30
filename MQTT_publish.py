#This code takes data and sends in to the AWS IoT core using MQTT
#This tutorial was used to connect raspberry pi with the aws IoT core -
#https://docs.aws.amazon.com/iot/latest/developerguide/connecting-to-existing-device.html

#This code is based on the -
#https://github.com/aws/aws-iot-device-sdk-python-v2/blob/main/samples/pubsub.py

from awscrt import mqtt
import sys
import threading
import time
from uuid import uuid4
import json
import datetime
import command_line_utils;

#get arguments from command line, yes its required, python crys when i try to replace this part....
cmdUtils = command_line_utils.CommandLineUtils("PubSub - Send and recieve messages through an MQTT connection.") 
cmdUtils.add_common_mqtt_commands()
cmdUtils.add_common_topic_message_commands()
cmdUtils.add_common_proxy_commands()
cmdUtils.add_common_logging_commands()
cmdUtils.register_command("key", "<path>", "Path to your key in PEM format.", True, str)
cmdUtils.register_command("cert", "<path>", "Path to your client certificate in PEM format.", True, str)
cmdUtils.register_command("port", "<int>", "Connection port. AWS IoT supports 443 and 8883 (optional, default=auto).", type=int)
cmdUtils.register_command("client_id", "<str>", "Client ID to use for MQTT connection (optional, default='test-*').", default="test-" + str(uuid4()))
cmdUtils.register_command("sensor_reading", "<str>", "Reading from the sensor to be uploaded.", str(uuid4()))
cmdUtils.get_args()

received_all_event = threading.Event()

#callbacks
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        print("Resubscribe results: {}".format(resubscribe_results))

        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))

def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    received_all_event.set()

#main function
if __name__ == '__main__':
    mqtt_connection = cmdUtils.build_mqtt_connection(on_connection_interrupted, on_connection_resumed)
    connect_future = mqtt_connection.connect()
    connect_future.result()
    subscribe_future, packet_id = mqtt_connection.subscribe(topic="sdk/test/Python",qos=mqtt.QoS.AT_LEAST_ONCE,callback=on_message_received)
    subscribe_result = subscribe_future.result()
    message = "{} [{}]".format(cmdUtils.get_command("sensor_reading"), datetime.datetime.now()) #that the data from terminal and add datatime to it
    message_json = json.dumps(message)
    mqtt_connection.publish(topic="sdk/test/Python",payload=message_json,qos=mqtt.QoS.AT_LEAST_ONCE) #send data in JSON fames to this topic

    time.sleep(1)
    if not received_all_event.is_set(): #wait for the message to be received
        print("Waiting for all messages to be received...")
    received_all_event.wait()

    disconnect_future = mqtt_connection.disconnect() # disconnect
    disconnect_future.result()
    print("Disconnected!")