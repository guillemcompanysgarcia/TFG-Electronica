import tkinter as tk
import tkinter.ttk as ttk
from ttkthemes import ThemedTk
import serial.tools.list_ports
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
import struct
import time
import threading

INTERVAL_PRECISION_ON = 2
INTERVAL_PRECISION_OFF = 1
INTERVAL_BARREJA_ON = 0.5
INTERVAL_BARREJA_OFF = 0.5

device_id = 0xC0
pump_cycle_thread = None
mix_cycle_thread = None
lock = threading.Lock()

desired_state = "Off"
desired_direction = "Right"
current_mode = "Predefined Mode"

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

def enable_485_communication(client, device_id):
    result = client.write_coil(0x1004, 0xFF00, device_id)
    print("Enabled 485 communication. \nModbus Info:", result)

def start_pump(client, device_id):
    result = client.write_coil(0x1001, 0xFF00, device_id)
    print("Started the pump. \nModbus Info:", result)

def stop_pump(client, device_id):
    result = client.write_coil(0x1001, 0x0000, device_id)
    print("Stopped the pump. \nModbus Info:", result)

def read_pump_state(client, device_id):
    result = client.read_coils(0x1001, 1, device_id)
    if result.isError():
        print("Error reading pump state. \nModbus Info:", result)
        return None
    if result.bits[0]:
        state = 'On'
    else:
        state = 'Off'

    #print(f"Current Pump state: {state}. \nModbus Info:", result)
    return state

def set_pump_speed(client, device_id, speed):
    speed = float(speed)
    speed_bytes = struct.pack('>f', speed)
    speed_high = speed_bytes[0] << 8 | speed_bytes[1]
    speed_low = speed_bytes[2] << 8 | speed_bytes[3]
    result = client.write_registers(0x3001, [speed_high, speed_low], device_id)
    print(f"Set pump speed to {speed:.2f} ml/min. \nModbus Info:", result)

def read_pump_speed(client, device_id):
    result = client.read_holding_registers(0x3001, 2, device_id)
    speed_bytes = struct.pack('>HH', result.registers[0], result.registers[1])
    speed = struct.unpack('>f', speed_bytes)[0]

    #print(f"Current Pump speed: {speed:.2f} ml/min. \nModbus Info:", result)
    return speed

def set_pump_direction(client, device_id, direction):
    if direction == 'Left':
        value = 0x0000
    elif direction == 'Right':
        value = 0xFF00
    else:
        print("Invalid direction. Use 'Left' or 'Right'.")
        return

    result = client.write_coil(0x1003, value, device_id)
    print(f"Set pump direction to {direction}. \nModbus Info:", result)

def change_direction(client, device_id):

    current_direction = read_pump_direction(client, device_id)
    new_direction = "Right" if current_direction == "Left" else "Left"
    stop_pump(client, device_id)
    set_pump_direction(client, device_id, new_direction)
 
def read_pump_direction(client, device_id):
    result = client.read_coils(0x1003, 1, device_id)
    if result.bits[0]:
        direction = 'Right'
    else:
        direction = 'Left'

    #print(f"Current Pump direction: {direction} \nModbus Info:", result)
    return direction

def pump_cycle(client, device_id, mode_var, on_duration, off_duration):
    global pump_cycle_thread
    pump_cycle_thread = threading.currentThread()
    mode = mode_var.get()

    while getattr(pump_cycle_thread, "do_run", True) and mode == "Precision Mode":
        start_pump(client, device_id)
        time.sleep(on_duration)
        stop_pump(client, device_id)
        time.sleep(off_duration)

def mix_cycle(client, device_id, mode_var, on_duration, off_duration):
    global mix_cycle_thread
    mix_cycle_thread = threading.currentThread()
    mode = mode_var.get()

    while getattr(mix_cycle_thread, "do_run", True) and mode == "Mix Mode":
        start_pump(client, device_id)
        time.sleep(on_duration)
        change_direction(client, device_id)
        stop_pump(client, device_id)
        time.sleep(off_duration)  

def on_start_stop_click(client, device_id, mode_var, interval_var, direction_var,  button, reset):
    global pump_cycle_thread
    global mix_cycle_thread

    global desired_state
    global desired_direction
    button['state'] = 'disabled'  # disable the button

    result = read_pump_state(client, device_id)
    mode = mode_var.get()

    if not reset:
        desired_state = "Off" if desired_state == "On" else "On"


    if desired_state == "On":
        current_direction = direction_var.get().split(':')[-1].strip()
        if current_direction != desired_direction:
            change_direction(client, device_id)
        if mode == "Predefined Mode":
            
            if result == "Off":
                start_pump(client, device_id)
        elif mode == "Precision Mode":
            on_duration, off_duration = map(float, interval_var.get().split(","))
            existing_thread = None

            # Check if a thread with the same name already exists
            for t in threading.enumerate():
                if t.name == "pump_cycle_thread":
                    existing_thread = t
                if t.name == "mix_cycle_thread":
                    t.do_run = False
            
            if existing_thread is not None and existing_thread.is_alive():
                existing_thread.do_run = True
            else:
                pump_cycle_thread = threading.Thread(target=pump_cycle, args=(client, device_id, mode_var, on_duration, off_duration), name="pump_cycle_thread")
                pump_cycle_thread.do_run = True
                pump_cycle_thread.start()    
            

        elif mode == "Mix Mode":
            on_duration, off_duration = map(float, interval_var.get().split(","))
            existing_thread = None

            # Check if a thread with the same name already exists
            for t in threading.enumerate():
                if t.name == "mix_cycle_thread":
                    existing_thread = t
                if t.name == "pump_cycle_thread":
                    t.do_run = False
            
            if existing_thread is not None and existing_thread.is_alive():
                existing_thread.do_run = True
            else:
                mix_cycle_thread = threading.Thread(target=mix_cycle, args=(client, device_id, mode_var, on_duration, off_duration), name="mix_cycle_thread")
                mix_cycle_thread.do_run = True
                mix_cycle_thread.start()
    else:
        if mode in ["Predefined Mode", "Precision Mode", "Mix Mode"]:
            if pump_cycle_thread is not None and pump_cycle_thread.is_alive():
                pump_cycle_thread.do_run = False
            if mix_cycle_thread is not None and mix_cycle_thread.is_alive():
                mix_cycle_thread.do_run = False

            if result == "On":
                stop_pump(client, device_id)

             
    button.after(500, lambda: button.config(state='normal'))
       
    
def on_direction_radio_click(client, device_id, mode_var, interval_var, direction_var,  button):
    global desired_direction
    desired_direction = "Left" if desired_direction == "Right" else "Right"
    if mode_var.get() in ["Predefined Mode", "Precision Mode"]:
        change_direction(client, device_id)
        on_start_stop_click(client, device_id, mode_var, interval_var, direction_var, button, 1)

def update_direction_radio_buttons(mode_var, right_button, left_button):
    if mode_var.get() in ["Predefined Mode", "Precision Mode"]:
        right_button["state"] = "normal"
        left_button["state"] = "normal"
    else:
        right_button["state"] = "disabled"
        left_button["state"] = "disabled"

def on_mode_select_click(client, mode_var, mode_combobox, interval_var, direction_var, button, right_button, left_button):
    global current_mode 
    global pump_cycle_thread
    global mix_cycle_thread
    selected_mode = mode_combobox.get()

    if selected_mode == "Predefined Mode":
        pass
    elif selected_mode == "Precision Mode":
        interval_var.set(f"{INTERVAL_PRECISION_ON}, {INTERVAL_PRECISION_OFF}")
    elif selected_mode == "Mix Mode":
        interval_var.set(f"{INTERVAL_BARREJA_ON}, {INTERVAL_BARREJA_OFF}")
    else:
        print("Invalid mode selected")

    with lock:
        # Stop the existing thread if it's running
        if pump_cycle_thread is not None and pump_cycle_thread.is_alive():
            pump_cycle_thread.do_run = False
        if mix_cycle_thread is not None and mix_cycle_thread.is_alive():
                mix_cycle_thread.do_run = False
        # If the pump is running and the mode has changed, restart the pump cycle
        if desired_state == "On" and selected_mode != current_mode:
            on_start_stop_click(client, device_id, mode_var, interval_var, direction_var, button, 1)

    current_mode = selected_mode  # Update the current_mode variable

    # Update the direction radio buttons state depending on the mode
    update_direction_radio_buttons(mode_var, right_button, left_button)

def on_speed_entry_submit(client, device_id, speed_entry, speed_scale):
    try:
        speed = float(speed_entry.get())
        if 1 <= speed <= 400:
            set_pump_speed(client, device_id, speed)
            speed_scale.set(speed)
        else:
            print("Invalid speed. Speed must be between 1 and 400.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")

def set_pump_speed_and_update_entry(client, device_id, new_speed, entry):
    # Check if the new speed is different from the current speed
    entry_value = entry.get()
    if entry_value == "":
        current_speed = 0
    else:
        current_speed = float(entry_value)
    
    new_speed = float(new_speed)

    if new_speed != current_speed:
        # Set the pump speed
        set_pump_speed(client, device_id, new_speed)

    # Update the entry widget with the new speed
    entry.delete(0, tk.END)
    entry.insert(0, str(int(new_speed)))

def update_labels(root, client, device_id, state_var, direction_var, speed_var):
    try:
        state = read_pump_state(client, device_id)
        direction = read_pump_direction(client, device_id)
        speed = read_pump_speed(client, device_id)

        state_var.set(f"Pump State: {state}")
        direction_var.set(f"Pump Direction: {direction}")
        speed_var.set(f"Pump Speed: {speed:.2f} rpm")
    except Exception as e:
        print("Error Updating Status"+ str(e))

    
    root.after(500, update_labels, root, client, device_id, state_var, direction_var, speed_var)

def main():
    '''actuators_port, sensors_port = find_Ports()
    if actuators_port is not None:
        actuators_client = ModbusSerialClient(
            method="rtu",
            port= actuators_port,
            baudrate=9600,
            stopbits=1,
            bytesize=8,
            parity="N",
            timeout=1
        )


        if actuators_client.connect():
            enable_485_communication(actuators_client, device_id)
            stop_pump(actuators_client, device_id)
            set_pump_direction(actuators_client, device_id, "Right")
            set_pump_speed(actuators_client, device_id, 100)'''

    actuators_client = " "
    # Create the main window
    root = ThemedTk(theme="arc") 
    root.title("Pump Control Panel")

    # Create labels for displaying state, direction, and speed
    state_var = tk.StringVar()
    direction_var = tk.StringVar()
    speed_var = tk.StringVar()
    #mode_var = 

    state_label = ttk.Label(root, textvariable=state_var)
    direction_label = ttk.Label(root, textvariable=direction_var)
    speed_label = ttk.Label(root, textvariable=speed_var)

    state_label.pack(fill=tk.X, padx=5, pady=5)
    direction_label.pack(fill=tk.X, padx=5, pady=5)
    speed_label.pack(fill=tk.X, padx=5, pady=5)

    # Create buttons
    start_stop_button = tk.Button(root, text="Start/Stop Pump", command=lambda: on_start_stop_click(actuators_client, device_id, mode_var, interval_var, direction_var, start_stop_button, 0))
    start_stop_button.pack(fill=tk.X, padx=5, pady=5)

    radio_direction_var = tk.StringVar()  # Create a new variable for radio buttons
    radio_direction_var.set("Right")

    # Add a title for the direction radio buttons
    direction_title = ttk.Label(root, text="Change Direction")
    direction_title.pack(fill=tk.X, padx=5, pady=5)
    right_button = tk.Radiobutton(root, text="Right", variable=radio_direction_var, value="Right",
                                command=lambda: on_direction_radio_click(actuators_client, device_id, mode_var, interval_var, direction_var, start_stop_button))
    left_button = tk.Radiobutton(root, text="Left", variable=radio_direction_var, value="Left",
                                command=lambda: on_direction_radio_click(actuators_client, device_id, mode_var, interval_var, direction_var, start_stop_button))
    
    right_button.pack(fill=tk.X, padx=5, pady=5)
    left_button.pack(fill=tk.X, padx=5, pady=5)
    
    speed_entry_label = ttk.Label(root, text="Enter Speed:")
    speed_entry_label.pack(fill=tk.X, padx=5, pady=5)

    speed_entry = ttk.Entry(root)
    speed_entry.insert(1, "1")  # Set placeholder value to 1
    speed_entry.pack(fill=tk.X, padx=5, pady=5)

    # Add min and max value labels
    min_value_label = ttk.Label(root, text="1")
    max_value_label = ttk.Label(root, text="400")

    # Place the min and max value labels on each side of the scale
    min_value_label.pack(side=tk.LEFT, padx=(5, 0), pady=5)
    max_value_label.pack(side=tk.RIGHT, padx=(0, 5), pady=5)

    speed_scale = ttk.Scale(root, from_=1, to=400, orient=tk.HORIZONTAL,
                            command=lambda value: set_pump_speed_and_update_entry(actuators_client, device_id, value, speed_entry))
    speed_scale.pack(fill=tk.X, padx=5, pady=5)

    speed_entry_submit_button = tk.Button(root, text="Set Speed", command=lambda: on_speed_entry_submit(actuators_client, device_id, speed_entry, speed_scale))
    speed_entry_submit_button.pack(fill=tk.X, padx=5, pady=5)

    # Create mode selection combobox
    mode_label = ttk.Label(root, text="Select Mode:")
    mode_label.pack(fill=tk.X, padx=5, pady=5)

    interval_var = tk.StringVar(root)
    interval_var.set("N/A")  # Valor inicial

    mode_var = tk.StringVar(root)
    mode_var.set("Predefined Mode")
    mode_option = ttk.Combobox(root, textvariable=mode_var, values=("Predefined Mode", "Precision Mode", "Mix Mode"), state="readonly")
    mode_option.pack(fill=tk.X, padx=5, pady=5)
    
    mode_option.bind("<<ComboboxSelected>>", lambda event: on_mode_select_click(actuators_client, mode_var, mode_option, interval_var, direction_var, start_stop_button, right_button, left_button))
    # Schedule the first update_labels call
    update_labels(root, actuators_client, device_id, state_var, direction_var, speed_var)
    update_direction_radio_buttons(mode_var, right_button, left_button)
    # Run the GUI
    root.mainloop()



if __name__ == "__main__":
    main()