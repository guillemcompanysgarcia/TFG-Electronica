# -*- coding: utf-8 -*-
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import time
import sys

from globals import config_obj, logging

def setup():
    try:
        DDBB_config = config_obj["InfluxDB"]

        global token, org, url, client, write_api
        token = DDBB_config.get("token")
        org = DDBB_config.get("org")
        url = DDBB_config.get("url")

        client = InfluxDBClient(url=url, token=token, org=org)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        del client
        logging.info("Correct INFLUXDB setup")

    except Exception as e:
        logging.error("Error during INFLUXDB setup", e)
        sys.exit(1)


def write_point(client_bucket, data):
    try:
        point = (
            Point(data['sensor_name'])
            .tag('Type', data['sensor_type'])
            .tag('Unit', data['sensor_unit'])
            .field('Value', float(data['sensor_reading']))
            .time(datetime.utcnow(), WritePrecision.S)
        )
        global write_api, org
        write_api.write(client_bucket, org, point)
        logging.info(f"Data point written successfully. Client: {client_bucket}; Sensor Name: {data['sensor_name']}; Type: {data['sensor_type']}; Value: {data['sensor_reading']} {data['sensor_unit']}")
    except Exception as e:
        logging.error(f"Error while trying to write point: {e}")
    finally:
        time.sleep(0.25)