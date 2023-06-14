from datetime import datetime
import json
from Sensor_class import Sensor
from Actuator_class import Actuator
from Alarm_class import Alarm
from globals import logging

import MODBUS_library as MODBUS
import MQTT_library as MQTT
import Camera_library as CAMERA
import Email_library as EMAIL

from operator import gt, lt, eq
from collections import deque

import random

OPERATION_MAP = {
    "Superior": gt,
    "Inferior": lt,
    "Igual": eq
}

MQTT_client = MQTT.setup()
MODBUS_Sensors_client, MODBUS_Actuators_client = MODBUS.setup()
camera = CAMERA.setup()
EMAIL.setup()

readings_dict = None

def set_readings_dict(new_readings_dict):
    global readings_dict
    readings_dict = new_readings_dict
def set_actuators(new_actuators_list):
    global actuators_list
    actuators_list = new_actuators_list
def set_sensors(new_sensors_list):
    global sensors_list
    sensors_list = new_sensors_list
def create_readings_dict(feasible_alarms):
    readings_dict = {}

    for alarm in feasible_alarms:
        if hasattr(alarm, 'associated_sensors'):
            for sensor in alarm.associated_sensors:
                max_cycles = max(condition['cycles'] for condition in alarm.conditions if condition['sensor'] == sensor['name'])
                if sensor['name'] not in readings_dict or max_cycles > len(readings_dict[sensor['name']]):
                    readings_dict[sensor['name']] = deque(maxlen=max_cycles)
        if hasattr(alarm, 'samples_sensor'):
            sensor = alarm.samples_sensor
            if sensor['name'] not in readings_dict or alarm.samples > len(readings_dict[sensor['name']]):
                readings_dict[sensor['name']] = deque(maxlen=alarm.samples)
    return readings_dict

def load_sensors(config_sensors):
    config_sensors = json.loads(config_sensors)
    sensor_list = list()

    for sensor in config_sensors:
        sensor_list.append(Sensor(sensor))

    return sensor_list

def load_actuators(config_actuators):
    config_actuators = json.loads(config_actuators)
    actuator_list = list()
    for actuator in config_actuators:
        actuator_list.append(Actuator(actuator))

    return actuator_list

def load_alarms(config_alarms):
    config_alarms = json.loads(config_alarms)
    alarm_list = list()

    for alarm in config_alarms:
        associated_sensors = []
        associated_actuators = []

        for condition in alarm.get("Condicions", []):
            sensor_name = condition.get("Sensor Associat")
            sensor_type = condition.get("Tipus")
            associated_sensors.append({'name': sensor_name, 'type': sensor_type})


        if alarm.get("Sensor a llegir") and alarm.get("Sensor a llegir") not in associated_sensors:
            associated_sensors.append(alarm.get("Sensor a llegir"))

        actuators_info = alarm.get("Actuadors Associats", []) or alarm.get("Actuador Associat")
        if actuators_info:
            for actuator_info in actuators_info:
                    actuator_name, actuator_type = actuator_info.split(" (")
                    associated_actuators.append({'name': actuator_name.strip(), 'type': actuator_type.replace(")", "").strip()})

        alarm_list.append(Alarm(alarm, associated_sensors, associated_actuators))

    return alarm_list
    
def review_alarms(alarms, sensors, actuators):
    feasible_alarms = list()
    not_feasible_alarms = list()
    
    available_sensors = [{'name': sensor.name, 'type': sensor.type} for sensor in sensors]
    available_actuators = [{'name': actuator.name, 'type': actuator.type} for actuator in actuators]

    for alarm in alarms:
        sensor_feasible = not hasattr(alarm, 'associated_sensors') or \
                  all(sensor in available_sensors for sensor in alarm.associated_sensors)
                          
        sensor_samples_feasible = not hasattr(alarm, 'samples_sensor') or \
                                   alarm.samples_sensor in available_sensors
                                   
        actuator_feasible = not hasattr(alarm, 'associated_actuators') or \
                    all(actuator in available_actuators for actuator in alarm.associated_actuators)

        if sensor_feasible and sensor_samples_feasible and actuator_feasible:
            feasible_alarms.append(alarm)
        else:
            not_feasible_alarms.append(alarm)
    
    return feasible_alarms, not_feasible_alarms

def condition_satisfied(condition, readings):
    operation = OPERATION_MAP[condition['comparison']]
    return all(operation(reading, condition['threshold']) for reading in readings)

def check_alarms(sensor_name, readings_dict, feasible_alarms):
    relevant_alarms = [alarm for alarm in feasible_alarms if sensor_name in alarm.get_associated_sensor_names()]

    triggered_alarms = {alarm.name: alarm for alarm in relevant_alarms}

    for alarm in relevant_alarms:
        triggered = False
        if alarm.trigger == "Condició":
            conditions_met = []
            for condition in alarm.conditions:
                condition_sensor = condition['sensor']
                readings = readings_dict[condition_sensor]
                if len(readings) < condition['cycles']:
                    continue
                conditions_met.append(condition_satisfied(condition, readings))

            if conditions_met and all(conditions_met):
                triggered = True
                
        if not triggered:
            del triggered_alarms[alarm.name]

    return list(triggered_alarms.values())

def fire_alarm(alarm):
    action = alarm.action
    if action == "Activar actuador" or action == "Desactivar actuador":
        handle_actuator_action(alarm, action)
    elif action == "Prendre una fotografia":
        handle_photo_action(alarm)
    elif action == "Enviar un correu electrònic":
        handle_email_action(alarm)
    else:
        logging.warning(f"Unsupported action: {action}")
        
def handle_actuator_action(alarm, action):
    for actuator in alarm.associated_actuators:
        try:
            if action == "Activar actuador":
                activate_actuator(actuator)
                logging.info("Actuator activated: " + actuator["name"])
            elif action == "Desactivar actuador":
                deactivate_actuator(actuator)
                logging.info("Actuator deactivated: "+ actuator["name"])
        except Exception as e:
            logging.warning(f"Error {action.lower()} actuator " + actuator.name, e)

def activate_actuator(to_fire_actuator):

    try:
        global actuators_list
        actuator = next((actuator for actuator in actuators_list if actuator.name == to_fire_actuator["name"] and actuator.type == to_fire_actuator["type"]), None)

        if actuator != None:
            Function, Address, Value = actuator.getModbusValues("Activar actuador")
            modbus_function(Modbus_Client = MODBUS_Actuators_client, func = Function, device_id = int(actuator.id), address = Address, value = Value)

    except Exception as e:
        logging.warning("Error activating actuator", actuator.name, e)

def deactivate_actuator(to_fire_actuator):
    try:
        global actuators_list
        actuator = next((actuator for actuator in actuators_list if actuator.name == to_fire_actuator["name"] and actuator.type == to_fire_actuator["type"]), None)

        if actuator != None:
            Function, Address, Value = actuator.getModbusValues("Desactivar actuador")
            modbus_function(Modbus_Client = MODBUS_Actuators_client, func = Function, device_id = actuator.id, address = Address, value = Value)

    except Exception as e:
        logging.warning("Error deactivating actuator", actuator.name, e)

def handle_photo_action(alarm):
    try:
        if camera:
            image_path = CAMERA.take_picture(camera)
        logging.info("Photo taken with Picamera")
        perform_postaction(alarm, image_path)
    except Exception as e:
        logging.warning("Error taking a photo with Picamera", e)

def perform_postaction(alarm, image_path):
    if hasattr(alarm, "postaction"):
        try:
            if alarm.postaction == "Guardar imatge localment":
                logging.info("Saving photo locally")
            elif alarm.postaction == "Enviar per correu electrònic":
                EMAIL.send_email_with_attachment(alarm.name, image_path, "template_image.html", "subject_image")
                logging.info("Sending photo via email")
            elif alarm.postaction == "Fer correlació de la mescla":
                correlation_path = CAMERA.correlate_image(image_path)
                logging.info("Correlating the mixture")
                perform_consecutive_action(alarm, correlation_path)
        except Exception as e:
            logging.warning(f"Error executing postaction {alarm.postaction}", e)

def perform_consecutive_action(alarm, correlation_result):
    if hasattr(alarm, "consecutive_action"):
        try:
            if alarm.consecutive_action == "Guardar informe correlació localment":
                logging.info("Saving correlation report locally")
            elif alarm.consecutive_action == "Enviar informe per correu electrònic":
                EMAIL.send_email_with_attachment(alarm.name, correlation_result, "template_correlation.html", "subject_correlation")
                logging.info("Sending correlation report via email")
        except Exception as e:
            logging.warning(f"Error executing consecutive action {alarm.consecutive_action}", e)

def handle_email_action(alarm):
    if hasattr(alarm, "samples") and hasattr(alarm, "samples_sensor"):
        try:
            global sensors_list
            global readings_dict

            sensor = next((sensor for sensor in sensors_list if sensor.name == alarm.samples_sensor["name"] and sensor.type == alarm.samples_sensor["type"]), None)

            if sensor is not None and sensor.name in readings_dict:
                if len(readings_dict[sensor.name]) >= alarm.samples:
                    if alarm.samples == 1:
                        value = readings_dict[sensor.name][-1]
                        EMAIL.send_email_with_reading(sensor_name=alarm.samples_sensor["name"],
                                                      sensor_type=alarm.samples_sensor["type"],
                                                      unit = sensor.unit,
                                                      value = value,
                                                      alarm_name=alarm.name,
                                                      subject = "subject_U_M")
                        logging.info("Sending email with a reading")
                    else:
                        values = list(readings_dict[sensor.name])[-alarm.samples:]
                        EMAIL.send_email_with_N_readings(sensor_name=alarm.samples_sensor["name"],
                                                        sensor_type=alarm.samples_sensor["type"],
                                                        unit = sensor.unit,
                                                        values = values,
                                                        alarm_name=alarm.name,
                                                        subject = "subject_N_M")
                        logging.info("Sending email with N readings")
                else:
                    logging.warning(f"Not enough samples ({len(readings_dict[sensor.name])}) to send email for sensor {sensor.name}")
        except Exception as e:
            logging.warning("Error sending email with a reading", e)
    else:
        logging.warning("Error: No samples or samples_sensor attribute found in the alarm object")


def read_sensor(sensor):
    result = 0
    try:
        result = modbus_function(Modbus_Client = MODBUS_Sensors_client, func = sensor.check_Modbusfunction(), device_id = 1, address = sensor.check_Address(), registers = sensor.check_Registercount())

        logging.info(
            "Measure of sensor "
            + sensor.check_Name()
            + ": "
            + str(result)
        )
        return result
    except Exception as e:
        logging.warning("Error reading sensor ", sensor.check_Name(), e)

def modbus_function(Modbus_Client, func, device_id, address, registers = 1, value = None):
    modbus_functions = {
        1: MODBUS.Function01,
        2: MODBUS.Function02,
        3: MODBUS.Function03,
        4: MODBUS.Function04,
        5: MODBUS.Function05,
        16: MODBUS.Function16
    }
    
    if func not in modbus_functions:
        raise ValueError(f"Unsupported MODBUS function code: {func}")
    
    if func in [1, 2, 3, 4]:
        result = modbus_functions[func](client = Modbus_Client, slave_id = device_id, address = address, num_registers = registers)
        logging.info("Reading sensor...")
        #result = None
        return result
    if func in [5, 16]:
        modbus_functions[func](client = Modbus_Client, slave_id = device_id, address = address, value = value)
        logging.info("Using actuator...")

def sensor_driven_alarm_block(sensor, s, alarms):
    result = read_sensor(sensor)
    '''if sensor.name == "A":
        result = 7
    if sensor.name == "B":
        result = 2'''
    #result = round(random.uniform(0, 10), 2)
    global readings_dict
    if readings_dict and sensor.name in readings_dict:
        readings_dict[sensor.name].append(result)


    message_data = MQTT.prepare_point(sensor, result)
    MQTT.publish(MQTT_client, sensor.name,  message_data )

    s.enter(
        sensor.check_Timer(),
        1,
        sensor_driven_alarm_block,
        argument=(
            sensor,
            s,
            alarms,
        ),
    )

    triggered_alarms = check_alarms(sensor.check_Name(), readings_dict, alarms)

    for alarm in triggered_alarms:
            print("Firing alarm "+ alarm.name +" caused by sensor " + sensor.name)
            fire_alarm(alarm)

def timer_driven_alarm_block(alarm, s):
    print("Firing alarm "+ alarm.name + " (timer driven)")
    fire_alarm(alarm)
    
    s.enter(
        alarm.check_Timer(),
        1,
        timer_driven_alarm_block,
        argument=(
            alarm,
            s,
        ),
    )
