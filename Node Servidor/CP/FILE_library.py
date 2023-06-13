# -*- coding: utf-8 -*-
import hashlib
import os
import json
from MQTT_library import publish
from globals import configurations_folder_path, logging

def get_file_hash(file_path):
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
        return hashlib.md5(file_data).hexdigest()
    except Exception as e:
        logging.error(f"Error getting hash for file {file_path}: {e}")

def get_files_hashes():
    files_hashes = {}
    try:
        for root, dirs, files in os.walk(configurations_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                files_hashes[file_path] = get_file_hash(file_path)
    except Exception as e:
        logging.error(f"Error getting file hashes: {e}")
    if files_hashes == {}:
        logging.info("No clients found")
    return files_hashes

def get_client_name_and_config_type(file_path):
    try:
        rel_path = os.path.relpath(file_path, configurations_folder_path)
        client_name, config_file = os.path.split(rel_path)
        config_type = os.path.splitext(config_file)[0].split('_')[0]
        return client_name, config_type
    except Exception as e:
        logging.error(f"Error getting client name and config type for file {file_path}: {e}")

def send_file(file_path, MQTT_client):
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
        client_name, config_type = get_client_name_and_config_type(file_path)
        topic = f"client_configurations/{client_name}/{config_type}"
        message = None
        if file_data.decode('utf-8').strip() == "[]":
            message = {'conf': "None"}
        elif file_data.decode('utf-8').strip() != "":
            message = {'conf': file_data.decode('utf-8')}
        if message:
            publish(MQTT_client, topic, json.dumps(message))
            logging.info(f"Configuration {config_type.capitalize()} sent to {client_name}")
    except Exception as e:
        logging.error(f"Error sending {config_type} configuration to {client_name}: {e}")

def send_all_files(MQTT_client, files_hashes):
    try:
        if files_hashes != {}:
            for file_path in files_hashes.keys():
                send_file(file_path, MQTT_client)
            logging.info("Configuration sent to all nodes.")
        else:
            logging.info("No configuration sent to any node.")
    except Exception as e:
        logging.error(f"Error sending all files: {e}")

def check_and_send_files(MQTT_client, files_hashes):
    try:
        for file_path, file_hash in files_hashes.items():
            current_hash = get_file_hash(file_path)
            if current_hash != file_hash:
                send_file(file_path, MQTT_client)
                files_hashes[file_path] = current_hash
    except Exception as e:
        logging.error(f"Error checking and sending files: {e}")