import serial.tools.list_ports
from pymodbus.client import ModbusSerialClient

import tkinter as tk
import tkinter.ttk as ttk
from ttkthemes import ThemedTk
import serial.tools.list_ports
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
import struct


import random

def find_Port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'USB2.0-Ser!' in port.description:
            print(f"Modbus adapter found on {port.device}")
            return str(port.device)
    print("Modbus adapter not found")
    exit()



def read_temperature(client, device_id):

    result = client.read_input_registers(0x0001, 1, device_id)
    if result.isError():
        print("Error reading temperature. \nModbus Info:", result)
        return None
    
    temp_bytes = struct.pack('>H', result.registers[0])
    temperature = struct.unpack('>h', temp_bytes)[0] / 100
    print(f"Temperature: {temperature}°C")
    return temperature

def read_humidity(client, device_id):

    result = client.read_input_registers(0x0002, 1, device_id)
    if result.isError():
        print("Error reading humidity. \nModbus Info:", result)
        return None
    
    humidity_bytes = struct.pack('>H', result.registers[0])
    humidity = struct.unpack('>h', humidity_bytes)[0] / 100
    print(f"Humidity: {humidity}%")
    return humidity


def read_temperature_humidity(client, device_id):
    temperature = read_temperature(client, device_id)
    humidity = read_humidity(client, device_id)
    return temperature, humidity



def main():
    client = ModbusSerialClient(
        method="rtu",
        port=find_Port(),
        baudrate=9600,
        stopbits=1,
        bytesize=8,
        parity="O",
        timeout=1
    )

    device_id = 0x01

    if client.connect():
        # Create the main window
        root = ThemedTk(theme="arc") 
        root.title("Sensor Control Panel")

        # Create labels for displaying temperature and humidity
        temp_var = tk.StringVar()
        humidity_var = tk.StringVar()

        temp_label = ttk.Label(root, textvariable=temp_var)
        humidity_label = ttk.Label(root, textvariable=humidity_var)

        temp_label.pack(fill=tk.X, padx=5, pady=5)
        humidity_label.pack(fill=tk.X, padx=5, pady=5)

        def clear_fields():
            temp_var.set('')
            humidity_var.set('')

        # Create buttons for reading temperature and humidity
        read_temp_button = tk.Button(root, text="Read Temperature", command=lambda: [clear_fields(), root.after(500, lambda: temp_var.set(f"{round(read_temperature(client, device_id), 2)} °C"))])
        read_temp_button.pack(fill=tk.X, padx=5, pady=5)

        read_humidity_button = tk.Button(root, text="Read Humidity", command=lambda: [clear_fields(), root.after(500, lambda: humidity_var.set(f"{round(read_humidity(client, device_id), 2)} %"))])
        read_humidity_button.pack(fill=tk.X, padx=5, pady=5)

        read_both_button = tk.Button(root, text="Read Both", command=lambda: [clear_fields(), root.after(500, lambda: [temp_var.set(f"{round(read_temperature(client, device_id), 2)} °C"), humidity_var.set(f"{round(read_humidity(client, device_id), 2)} %")])])
        read_both_button.pack(fill=tk.X, padx=5, pady=5)


        # Run the GUI
        root.mainloop()

if __name__ == "__main__":
    main()
