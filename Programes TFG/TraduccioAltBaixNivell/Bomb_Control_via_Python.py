import serial.tools.list_ports
from pymodbus.client import ModbusSerialClient
import struct

def find_Port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'USB-SERIAL CH340' in port.description:
            print(f"Modbus adapter found on {port.device}")
            return str(port.device)
    print("Modbus adapter not found")
    exit()

def enable_485_communication(client, device_id):
    result = client.write_coil(0x1004, 0xFF00, device_id)
    #result = client.write_coil(4100,65280,192)
    print("Enabled 485 communication. \nModbus Info:", result)

def start_pump(client, device_id):
    result = client.write_coil(0x1001, 0xFF00, device_id)
    print("Started the pump. \nModbus Info:", result)

def stop_pump(client, device_id):
    result = client.write_coil(0x1001, 0x0000, device_id)
    print("Stopped the pump. \nModbus Info:", result)

def set_pump_speed(client, device_id, speed):
    speed_bytes = struct.pack('>f', speed)
    speed_high = speed_bytes[0] << 8 | speed_bytes[1]
    speed_low = speed_bytes[2] << 8 | speed_bytes[3]
    result = client.write_registers(0x3001, [speed_high, speed_low], device_id)
    print(f"Set pump speed to {speed} rpm. \nModbus Info:", result)

def set_pump_direction(client, device_id, direction):
    if direction.lower() == 'positive':
        value = 0x0000
    elif direction.lower() == 'negative':
        value = 0xFF00
    else:
        print("Invalid direction. Use 'positive' or 'negative'.")
        return

    result = client.write_coil(0x1003, value, device_id)
    print(f"Set pump direction to {direction}. \nModbus Info:", result)

def empty_pump(client, device_id, action):
    if action.lower() == 'start':
        value = 0xFF00
    elif action.lower() == 'stop':
        value = 0x0000
    else:
        print("Invalid action. Use 'start' or 'stop'.")
        return

    result = client.write_coil(0x1002, value, device_id)
    print(f"Empty pump {action}. \nModbus Info:", result)

def read_pump_direction(client, device_id):
    result = client.read_coils(0x1003, 1, device_id)
    if result.bits[0]:
        direction = 'negative'
    else:
        direction = 'positive'

    print(f"Current Pump direction: {direction} \nModbus Info:", result)
    return direction

def read_pump_speed(client, device_id):
    result = client.read_holding_registers(0x3001, 2, device_id)
    speed_bytes = struct.pack('>HH', result.registers[0], result.registers[1])
    speed = struct.unpack('>f', speed_bytes)[0]

    print(f"Current Pump speed: {speed:.2f} rpm. \nModbus Info:", result)
    return speed

def read_pump_state(client, device_id):
    result = client.read_coils(0x1001, 1, device_id)
    if result.isError():
        print("Error reading pump state. \nModbus Info:", result)
        return None
    if result.bits[0]:
        state = 'on'
    else:
        state = 'off'

    print(f"Current Pump state: {state}. \nModbus Info:", result)
    return state

def main():
    client = ModbusSerialClient(
        method="rtu",
        port=find_Port(),
        baudrate=9600,
        stopbits=1,
        bytesize=8,
        parity="N",
        timeout=1
    )

    device_id = 0xC0

    if client.connect():
        enable_485_communication(client, device_id)

        while True:
            
            print("\nCommands:")
            print("1. Start the pump")
            print("2. Stop the pump")
            print("3. Set pump speed")
            print("4. Set pump speed and restart pump")
            print("5. Change pump direction")
            print("6. Change pump direction and restart pump")
            print("7. Empty the pump")
            print("8. Read pump direction")
            print("9. Read pump speed")
            print("10. Read pump state")
            print("q. Quit")

            user_input = input("\nEnter the command: ").lower()
            print(f"\nCommand entered: {user_input}")

            if user_input == '1':
                result = read_pump_state(client, device_id)
                if result == 'off':
                    start_pump(client, device_id)
                else:
                    print("Pump already on")

            elif user_input == '2':
                result = read_pump_state(client, device_id)
                if result == 'on':
                    stop_pump(client, device_id)
                else:
                    print("Pump already off")  

            elif user_input == '3':
                speed = float(input("\nEnter the new speed (rpm): "))
                result = read_pump_speed(client, device_id)
                if result != speed:
                    set_pump_speed(client, device_id, speed)
                else:
                    print(f"Current speed is already: {speed:.2f} rpm")
            
            elif user_input == '4':
                speed = float(input("\nEnter the new speed (rpm): "))
                result = read_pump_speed(client, device_id)
                result2 = read_pump_state(client, device_id)
                if result != speed:
                    if result2 == 'on':
                        stop_pump(client, device_id)
                        set_pump_speed(client, device_id, speed)
                        start_pump(client,device_id)
                    else:
                        set_pump_speed(client, device_id, speed)
                        start_pump(client,device_id)
                else:
                    print(f"Current speed is already: {speed:.2f} rpm")

            elif user_input == '5':
                current_direction = read_pump_direction(client, device_id)
                
                if current_direction is not None:
                    if current_direction == 'positive':
                        new_direction = 'negative'
                    else:
                        new_direction = 'positive'
                    
                    set_pump_direction(client, device_id, new_direction)
            
            elif user_input == '6':
                current_direction = read_pump_direction(client, device_id)
                result = read_pump_state(client, device_id)
                if result == 'on':
                    stop_pump(client, device_id)

                if current_direction is not None:
                    if current_direction == 'positive':
                        new_direction = 'negative'
                    else:
                        new_direction = 'positive'
                    
                    set_pump_direction(client, device_id, new_direction)
                    start_pump(client,device_id)


            elif user_input == '7':
                action = (input("\nEmpty the pump: start or stop "))
                empty_pump(client, device_id, action)

            elif user_input == '8':
                read_pump_direction(client, device_id)

            elif user_input == '9':
                read_pump_speed(client, device_id)

            elif user_input == '10':
                read_pump_state(client, device_id)

            elif user_input == 'q':
                break

            else:
                print("\nInvalid command, please try again.")

        client.close()

if __name__ == "__main__":
    main()