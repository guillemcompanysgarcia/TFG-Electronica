# -*- coding: utf-8 -*-
import sys

import MQTT_library as MQTT
import INFLUXDB_library as INFLUXDB
import FILE_library as FILE

from globals import logging

def setup():
    MQTT_client =  MQTT.setup()
    INFLUXDB.setup()
    files_hashes = FILE.get_files_hashes()
    return MQTT_client, files_hashes

def main():
    try:
        MQTT_client, files_hashes = setup()
        logging.info("Program setup complete")
    except Exception as e:
        logging.critical("Critical error in program setup", e)
        sys.exit(1)

    FILE.send_all_files(MQTT_client, files_hashes)

    while True:
        while not MQTT.q.empty():
            new_measure = MQTT.q.get()
            if new_measure is not None:
                logging.info("New message recieved")
                client_bucket = new_measure.get("client_bucket")
                INFLUXDB.write_point(client_bucket, new_measure)

        FILE.check_and_send_files(MQTT_client, files_hashes)

if __name__ == "__main__":
    main()