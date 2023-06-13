## -*- coding: utf-8 -*-
import serial.tools.list_ports
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
import struct  # Import struct library which is used to unpack the data received from the Modbus slave device
from globals import config_obj, logging

def find_adapters():
    adapter_ports = []

    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'USB2.0-Ser!' in port.description:
            adapter_ports.append(str(port.device))

    if not adapter_ports:
        print("No Modbus adapters found")
        exit()

    return adapter_ports

def check_adapters(adapter_ports):
    actuators_port = None
    sensors_port = None

    for port in adapter_ports:
        client = ModbusSerialClient(method='rtu', port=port, baudrate=9600, stopbits=1, parity='N', bytesize=8, timeout=1)
        coil_address = 0x1004
        output_value = 0xFF00
        device_id = 0xC0
        try:
            response = client.write_coil(coil_address, output_value, device_id)
            if response.isError():
                raise ModbusException("Modbus error response")
            actuators_port = port
        except ModbusException as e:
            sensors_port = port
        finally:
            client.close()

    return actuators_port, sensors_port

def find_Ports():
    adapters = find_adapters()
    actuator_port, sensor_port = check_adapters(adapters)
    return actuator_port, sensor_port

def setup():
    actuators_port, sensors_port = find_Ports()
    if actuators_port is not None:
        MODBUS_Actuators_client = ModbusSerialClient(
            method="rtu",
            port= actuators_port,
            baudrate=9600,
            stopbits=1,
            bytesize=8,
            parity="N",
            timeout=1
        )
        if MODBUS_Actuators_client.connect():
            enable_485_communication(MODBUS_Actuators_client, 0xC0)
    if sensors_port is not None:
        MODBUS_Sensors_client = ModbusSerialClient(
            method="rtu",
            port= sensors_port,
            baudrate=9600,
            stopbits=1,
            bytesize=8,
            parity="O",
            timeout=1
        )    
    return MODBUS_Sensors_client, MODBUS_Actuators_client 


def Function01(client, slave_id, address, num_registers):  
    try:
        result = client.read_coils(
            address, num_registers, slave_id
        )  # sending command to read coils
        resultat = (
            parse_register(result.registers[0], 6)
            + parse_register(result.registers[1], 6).split("x")[1]
        )  # process the registers to be in hexa
        return hex_to_float(resultat)  # return the float

    except Exception as e:
        logging.warning("Error while reading coil status  ", e)


def Function02(client, slave_id, address, num_registers):
    try:
        result = client.read_discrete_inputs(
            address, num_registers, slave_id
        )  # sending command to read discrete inputs
        resultat = (
            parse_register(result.registers[0], 6)
            + parse_register(result.registers[1], 6).split("x")[1]
        )  # process the registers to be in hexa
        return hex_to_float(resultat)  # return the float

    except Exception as e:
        logging.warning("Error while reading input status  ", e)

def Function03(client, slave_id, address, num_registers):
    try:
        result = client.read_holding_registers(
            address, num_registers, slave_id
        )  # sending command to read holding registers
        resultat = (
            parse_register(result.registers[0], 6)
            + parse_register(result.registers[1], 6).split("x")[1]
        )  # process the registers to be in hexa
        return hex_to_float(resultat)  # return the float

    except Exception as e:
        logging.warning("Error while reading holding registers  ", e)


def Function04(client, slave_id, address, num_registers):
    try:
        result = client.read_input_registers(
            address, num_registers, slave_id
        )  # sending command to read input registers
        if num_registers > 1:
            resultat = (
                parse_register(result.registers[0], 6)
                + parse_register(result.registers[1], 6).split("x")[1]
            )  # process the registers to be in hexa
            return hex_to_float(resultat)  # return the float
        else:
            reading = result.registers[0] /100
            return reading

    except Exception as e:
        logging.warning("Error while reading input registers  ", e)

def enable_485_communication(client, device_id):
    device_id =0xC0
    result = client.write_coil(0x1004, 0xFF00, device_id)
    print("Enabled 485 communication. \nModbus Info:", result)

def Function05(client, slave_id, address, value):
    try:
        slave_id = 192
        client.write_coil(
            address, value, slave_id
        )  # sending command to write a single coil

    except Exception as e:
        logging.warning("Error while forcing a single coil  ", e)


def Function16(client, slave_id, address, values):
    try:
        client.write_registers(
            address, values, slave_id
        )  # sending command to write multiple registers

    except Exception as e:
        logging.warning("Error while presseting multiple registers  ", e)


def hex_to_float(hexa):
    return struct.unpack("!f", struct.pack("!I", int(hexa, 16)))[0]


def parse_register(reg, padding):
    return f"{reg:#0{padding}x}"
