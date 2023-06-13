# -*- coding: utf-8 -*-
import time
import sched
import sys

import MQTT_library as MQTT
import Control_library as Control

from globals import logging

def setup():
    s = sched.scheduler(time.time, time.sleep)
    return s

def main():
    try:
        s = setup()
    except Exception as e:
        logging.critical("Error in program setup", e)
        sys.exit(1)

    global sensors_list, actuators_list
    sensors_list = []
    actuators_list = []
    timer_driven_feasible_alarms = []
    sensor_driven_feasible_alarms = []
    received_configurations = {}
    configuration_updated = {"sensors": False, "actuators": False, "alarms": False}

    while True:
        s.run(blocking=False)

        while not MQTT.q.empty():
            new_config = MQTT.q.get()
            if new_config is not None:
                logging.info("New message received")

                if s.empty() is False:
                    list(map(s.cancel, s.queue))

                conf_type = new_config.get('conf_type')
                if received_configurations.get(conf_type) != new_config.get('conf'):
                    received_configurations[conf_type] = new_config.get('conf')
                    configuration_updated[conf_type] = True

            if all(key in received_configurations for key in ["sensors", "actuators", "alarms"]):
                
                if configuration_updated["sensors"]:
                    logging.info(f"New Sensors of the System: {received_configurations['sensors']}")
                    configuration_updated["sensors"] = False
                    sensors_list = []
                    if received_configurations["sensors"] != "None":
                        sensors_list = Control.load_sensors(received_configurations["sensors"])
                    
                if configuration_updated["actuators"]:
                    logging.info(f"New Actuators of the System: {received_configurations['actuators']}")
                    configuration_updated["actuators"] = False
                    actuators_list = []
                    if received_configurations["actuators"] != "None":
                        actuators_list = Control.load_actuators(received_configurations["actuators"])
                    
        
                if configuration_updated["alarms"]:
                    logging.info(f"New Alarms of the System: {received_configurations['alarms']}")
                    configuration_updated["alarms"] = False 
                    alarms_list = []
                    timer_driven_feasible_alarms = []
                    sensor_driven_feasible_alarms = []
                    if received_configurations["alarms"] != "None":
                        alarms_list = Control.load_alarms(received_configurations["alarms"])
                        feasible_alarms, not_feasible_alarms = Control.review_alarms(alarms_list,sensors_list,actuators_list)
                        readings_dict = Control.create_readings_dict(feasible_alarms)
                        Control.set_readings_dict(readings_dict)
                        Control.set_sensors(sensors_list)
                        Control.set_actuators(actuators_list)
                        for alarm in feasible_alarms:
                            logging.info(f"Alarm '{alarm.name}' can be successfully initialized.")
                        for alarm in not_feasible_alarms:
                            logging.warning(f"Cannot initialize alarm '{alarm.name}' because not all associated sensors or actuators are available")

                        
                        for alarm in feasible_alarms:
                            if alarm.trigger == "Alarma Recurrent":
                                timer_driven_feasible_alarms.append(alarm)
                            elif alarm.trigger == "Condició":
                                sensor_driven_feasible_alarms.append(alarm)
                        del feasible_alarms, not_feasible_alarms

                        for alarm in timer_driven_feasible_alarms:
                                s.enter(
                                    alarm.check_Timer(),
                                    1,
                                    Control.timer_driven_alarm_block,
                                    argument=(
                                        alarm,
                                        s,
                                    ),
                                )


                    if set(received_configurations.keys()) == {"sensors", "actuators", "alarms"}:
                        for sensor in sensors_list:
                            s.enter(
                                sensor.check_Timer(),
                                1,
                                Control.sensor_driven_alarm_block,
                                argument=(
                                    sensor,
                                    s,
                                sensor_driven_feasible_alarms,    
                                ),
                            )

                            
                    

if __name__ == "__main__":
    main()
