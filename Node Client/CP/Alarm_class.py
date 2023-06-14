from datetime import (
    datetime,
    timedelta,
)  # import the datetime and timedelta modules to work with dates and times

from collections import deque


class Alarm:
    def __init__(self, alarm_info, associated_sensors = None, associated_actuators = None):

        self.name = alarm_info["Nom de l'Alarma"]  # Alarm name
        self.id = alarm_info["Identificador"]  # Alarm identifier
        self.action = alarm_info["Acció"]  # Action to take when operation is performed
        self.trigger = alarm_info["Desencadenant"]
        
        
        if self.action == "Activar actuador"  and associated_actuators is not None:
            self.associated_actuators = associated_actuators
            self.mode = alarm_info.get("Mode Funcionament")

        elif self.action == "Desactivar actuador"  and associated_actuators is not None:
            self.associated_actuators = associated_actuators

        elif self.action == "Prendre una fotografia":
            self.postaction = alarm_info.get("Acció Posterior")
            if self.postaction == "Fer correlació de la mescla":
                self.consecutive_action = alarm_info.get("Acció Consecutiva")
            
        elif self.action == "Enviar un correu electrònic":
            if alarm_info.get("Nº mostres"):
                self.samples = int(alarm_info.get("Nº mostres"))
            if alarm_info.get("Sensor a llegir"):
                parts = alarm_info.get("Sensor a llegir").split(' (')
                
                name = parts[0]
                sensor_type = parts[1].rstrip(')')
                self.samples_sensor = {'name': name, 'type': sensor_type}

        if self.trigger == "Condició" and associated_sensors is not None:
            self.associated_sensors = associated_sensors
            parsed_conditions = []
            for condition in alarm_info.get("Condicions", []):
                parsed_condition = {
                    'sensor': condition['Sensor Associat'],
                    'type': condition['Tipus'],
                    'comparison': condition['Comparació'],
                    'threshold': float(condition['Valor Llindar']),
                    'unit': condition['Unitat'],
                    'cycles': int(condition['Nº cicles']),
                }
                parsed_conditions.append(parsed_condition)

            self.conditions = parsed_conditions
        elif self.trigger == "Alarma Recurrent":
            self.time_interval = self.calculate_interval(alarm_info.get("Interval"))   # Interval between alarm checks

        self.comments = alarm_info.get("Comentaris Addicionals o Observacions")  # Additional alarm comments

    def __str__(self):
        attrs = vars(self)
        return ', '.join("%s: %s" % item for item in attrs.items())
    
    def calculate_interval(self, interval_str):
        interval = int(interval_str.split()[0])
        return interval if 1 <= interval <= 600 else None
                
    def get_threshold(self): #A modificar
         return int(self.threshold.split()[0])
    
    def set_buffer_size(self, sensor): #A modificar
         self.circular_buffer = deque(maxlen=(self.duration_check//sensor.time_interval))
    
    def get_Modbus_values(self, open_valve): #A modificar
        modbus_function, address, value = self.associated_actuator.get_modbus_values(open_valve)
        return(modbus_function, address, value)
    ()
    def get_associated_sensor_names(self):
        sensor_names = []
        if hasattr(self, 'associated_sensors'):
            for sensor in self.associated_sensors:
                sensor_names.append(sensor['name'])

        return sensor_names
    
    def check_Timer(self):
        """
        Check the time interval of the sensor

        Returns:
            the time interval of the sensor
        """
        return self.time_interval