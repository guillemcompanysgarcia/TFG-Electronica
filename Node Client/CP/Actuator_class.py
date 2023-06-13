from globals import logging, Actuators_info



class Actuator:
    def __init__(self, actuator_info):
        self.name = actuator_info["Nom de l'Actuador"]  # Actuator name
        self.type = actuator_info["Tipus d'Actuador"]  # Actuator type
        self.id = actuator_info["Identificador"]  # Actuator id
        self.brand = actuator_info["Marca comercial"]  # Actuator brand
        self.model = actuator_info["Model"]  # Actuator model
        self.comments = actuator_info["Comentaris Addicionals"]  # Additional actuator comments

    def __str__(self):
        attrs = vars(self)
        return ', '.join("%s: %s" % item for item in attrs.items())
    
    def getModbusValues(self, action):
        
        if action == "Activar actuador":
            try:
                Function, Address, Value = Actuators_info[self.brand][self.model]["Start_Pump"][0].values()
                Function = int(Function)
                Address = int (Address, 16)
                Value = int(Value, 16)
                return Function, Address, Value
            except Exception as e:
                logging.warning("Error getting the correct modbus parameters while trying to activate the actuator "+ self.name, e)
        
        if action == "Desactivar actuador":
            try:
                Function, Address, Value = Actuators_info[self.brand][self.model]["Stop_Pump"][0].values()
                Function = int(Function)
                Address = int (Address, 16)
                Value = int(Value, 16)
                return Function, Address, Value
            except Exception as e:
                logging.warning("Error getting the correct modbus parameters while trying to deactivate the actuator "+ self.name, e)
         