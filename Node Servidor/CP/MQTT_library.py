# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import json
import sys

from queue import Queue
from globals import config_obj, logging

q = Queue()

def setup():
    try:
        MQTT_config = config_obj["MQTT"]

        global device, broker_address, subscribe_topic

        device = MQTT_config.get("device") 
        broker_address = MQTT_config.get("broker_address")
        subscribe_topic = MQTT_config.get("subscribe_topic")

        MQTT_client = connect()
        MQTT_client.subscribe(subscribe_topic, qos=2)
        MQTT_client.loop_start()
        logging.info("Correct MQTT setup")
        return MQTT_client
    except Exception as e:
        logging.error("Error during MQTT setup", e)
        sys.exit(1)

def on_message(client, userdata, message):
    try:
        JSON_message = str(message.payload.decode("utf-8"))
        sensor_measure = json_to_dict(JSON_message)
        client_name = message.topic.split('/')[1]
        sensor_measure["client_bucket"] = client_name
        q.put(sensor_measure)
    except Exception as e:
        logging.error(f"Error processing message: {e}")


def connect():
    try:
        client = mqtt.Client(device)
        client.on_message = on_message
        rc = client.connect(broker_address)
        if rc == 0:
            logging.info("Remote connection started with Mosquitto MQTT")
        else:
            logging.error(f"RC Error while trying to connect {rc}")
        return client
    except Exception as e:
        logging.error(f"E Error while trying to connect: {e}")

def publish(client, topic, message):
    try:
        status = client.publish(topic, message, qos=2, retain=True)
        if status[0] == 0:
            logging.info(f"Sending configuration to `{topic}`")
        else:
            logging.error(f"Failed to send configuration to {topic}, status: {status[0]}")
    except Exception as e:
        logging.error(f"Error while trying to publish: {e}")

def json_to_dict(JSON):
    try:
        dic = json.loads(JSON)
        return dic
    except json.JSONDecodeError as e:
        logging.error(f"Error while trying to convert JSON to dictionary: {e}")