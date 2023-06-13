import logging
from logging.handlers import RotatingFileHandler
import configparser
import os
import sys
import json

config_obj = configparser.ConfigParser()
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, "..", "Altres", "configfile.ini")
config_obj.read(config_file_path, encoding='utf-8')

json_path = os.path.join(script_dir, "..", "Altres", "Actuators.json")

with open(json_path, "r") as json_file:
    Actuators_info = json.load(json_file)

log_format = '%(asctime)s - %(levelname)s - %(message)s'
log_file_path = os.path.join(script_dir, "..", "Altres", "client.log")

stream_handler = logging.StreamHandler(sys.stdout)
rotating_handler = RotatingFileHandler(log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8')

logging.basicConfig(level=logging.INFO, format=log_format, handlers=[stream_handler, rotating_handler])
logging.info(f"Client Node starting...")