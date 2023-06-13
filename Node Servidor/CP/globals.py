import logging
from logging.handlers import RotatingFileHandler
import configparser
import os
import sys

config_obj = configparser.ConfigParser()
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, "..", "Altres", "configfile.ini")
config_obj.read(config_file_path, encoding='utf-8')

configurations_folder_path = os.path.join(script_dir,"..", "DS", "PW", "configurations")

log_format = '%(asctime)s - %(levelname)s - %(message)s'
log_file_path = os.path.join(script_dir, "..", "Altres", "server.log")

stream_handler = logging.StreamHandler(sys.stdout)
rotating_handler = RotatingFileHandler(log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8')

logging.basicConfig(level=logging.INFO, format=log_format, handlers=[stream_handler, rotating_handler])
logging.info(f"Server Node starting...")

