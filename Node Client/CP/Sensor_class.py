from datetime import (
    datetime,
    timedelta,
)  # import the datetime and timedelta modules to work with dates and times


class Sensor:
    def __init__(self, sensor_info):
        """
        Initializes the sensor with provided information

        Args:
            sensor_info: dictionary containing sensor information.
        """


        self.name = sensor_info['Nom del Sensor']  # Sensor name
        self.id = sensor_info['Identificador']  # Sensor identifier
        self.type = sensor_info['Tipus de Sensor']  # Sensor type
        self.unit = self.calculate_unit()
        self.id = sensor_info['Identificador']  # Sensor id
        self.time_interval = self.calculate_interval(sensor_info['Interval de Temps'])  # Sensor read interval
        self.modbus_function = self.calculate_ModbusFunc(
            sensor_info['Funció Modbus Lectura']
        )  # Modbus function to use with the sensor
        self.address = int(sensor_info["Adreça"])  # Sensor address
        self.register_count = int(
            sensor_info["Nº Registres"]
        )  # Number of registers to read
        self.comments = sensor_info["Comentaris Addicionals"]  # Additional sensor comments

    def __str__(self):
        attrs = vars(self)
        return ', '.join("%s: %s" % item for item in attrs.items())
    
    def check_Name(self):
        return self.name

    def check_Timer(self):
        return self.time_interval

    def check_Modbusfunction(self):
        return self.modbus_function

    def check_Address(self):
        return self.address

    def check_Registercount(self):
        return self.register_count

    def check_Type(self):
        return self.type
    
    def check_Unit(self):
        return self.unit

    def calculate_ModbusFunc(self, func):
        func_num = 0

        if func == "Function 01 (Read Coil Status)":
            func_num = 1
        if func == "Function 02 (Read Input Status)":
            func_num = 2
        if func == "Function 03 (Read Holding Registers)":
            func_num = 3
        if func == "Function 04 (Read Input Registers)":
            func_num = 4
        if func == "Function 05 (Force Single Coil)":
            func_num = 5
        if func == "Function 16 (Preset Multiple Registers)":
            func_num = 16

        return func_num


    def calculate_interval(self, interval):
                
        if interval == "Cada 5 segons":
            return 5
        if interval == "Cada 10 segons":
            return 10
        if interval == "Cada 15 segons":
            return 15
        if interval == "Cada 20 segons":
            return 20
        if interval == "Cada 25 segons":
            return 25
        if interval == "Cada 30 segons":
            return 30
        if interval == "Cada minut":
            return 60
                
    def calculate_unit(self):
        if self.type == "pH":
            return "pH"
        elif self.type == "Conductivitat":
            return "µS/cm"
        elif self.type == "ORP":
            return "mV"
        elif self.type == "Oxigen dissolt":
            return "mL/L"
        elif self.type == "Temperatura":
            return "ºC"
        elif self.type == "Humitat":
            return "%HR"
        else:
            print("Error calculant unitats")