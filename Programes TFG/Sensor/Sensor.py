import serial.tools.list_ports
from pymodbus.client import ModbusSerialClient
import struct

def find_Port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'USB2.0-Ser!' in port.description:
            print(f"Modbus adapter found on {port.device}")
            return str(port.device)
    print("Modbus adapter not found")
    exit()

def read_temperature_humidity(client, device_id):
    result = client.read_input_registers(0x001, 2, device_id)
    if result.isError():
        print("Error reading temperature and humidity. \nModbus Info:", result)
        return None, None

    temp_bytes = struct.pack('>H', result.registers[0])
    humidity_bytes = struct.pack('>H', result.registers[1])
    temperature = struct.unpack('>h', temp_bytes)[0] /100
    humidity = struct.unpack('>h', humidity_bytes)[0] /100

    print(f"Temperature: {temperature}°C, Humidity: {humidity}% \nModbus Info:", result)
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
        while True:
            print("\nCommands:")
            print("1. Read temperature and humidity")
            print("q. Quit")

            user_input = input("\nEnter the command: ").lower()
            print(f"\nCommand entered: {user_input}")

            if user_input == '1':
                read_temperature_humidity(client, device_id)

            elif user_input == 'q':
                break

            else:
                print("\nInvalid command, please try again.")

        client.close()

if __name__ == "__main__":
    main()
