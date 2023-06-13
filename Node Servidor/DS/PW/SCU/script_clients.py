import os
import sys

# Add the root directory to the Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)

from app import app, db, Client
from sqlalchemy import inspect

def print_all_clients():
    # Retrieve all clients from the database
    clients = Client.query.all()

    # Print each client's name and URL
    for client in clients:
        print(f"Name: {client.name}, Grafana URL: {client.sensors_panel}, Sensors URL: {client.data_base}, System Monitoring URL:{client.system_monitoring}")

def add_client():
    name = input("Enter the name of the client: ") or 'Chemplate'
    sensors_panel = input("Enter the Grafana URL for the client (default: https://www.grafana.com): ") or 'https://www.grafana.com'
    data_base = input("Enter the sensors URL for the client (default: https://www.influxdata.com): ") or 'https://www.influxdata.com'
    system_monitoring = input("Enter the system monitoring URL (default:  https://picockpit.com/mypis/login): ") or ' https://picockpit.com/mypis/login'


    existing_client = Client.query.filter_by(name=name).first()
    if existing_client:
        print(f"A client with the name {name} already exists.")
        return
        
    new_client = Client(name = name, sensors_panel = sensors_panel, data_base = data_base, system_monitoring = system_monitoring)

    db.session.add(new_client)
    db.session.commit()
    print("New client added successfully!")

def delete_client():
    name = input("Enter the name of the client to delete: ")
    client_to_delete = Client.query.filter_by(name=name).first()
    if client_to_delete:
        db.session.delete(client_to_delete)
        db.session.commit()
        print(f"Client {name} has been deleted.")
    else:
        print(f"No client found with name {name}.")

def modify_client():
    name = input("Enter the name of the client to modify: ")
    client_to_modify = Client.query.filter_by(name=name).first()
    if client_to_modify:
        new_name = input(f"Enter the new name for the client (leave blank to keep '{client_to_modify.name}'): ")
        new_sensors_panel = input(f"Enter the new Grafana URL for the client (leave blank to keep '{client_to_modify.sensors_panel}'): ")
        new_data_base = input(f"Enter the new sensors URL for the client (leave blank to keep '{client_to_modify.data_base}'): ")
        new_system_monitoring = input(f"Enter the new system monitoring URL for the client (leave blank to keep '{client_to_modify.system_monitoring}'): ")

        if new_name:
            client_to_modify.name = new_name
        if new_sensors_panel:
            client_to_modify.sensors_panel = new_sensors_panel
        if new_data_base:
            client_to_modify.data_base = new_data_base
        if new_system_monitoring:
            client_to_modify.system_monitoring = new_system_monitoring

        db.session.commit()
        print(f"Client {name} has been modified.")
    else:
        print(f"No client found with name {name}.")

def main():
    app.app_context().push()

    db.create_all()
    
    while 1:
        answer = input("Do you want to add a new client (a), delete a client (d), modify a client (m), or view all clients (v)? ")
        if answer.lower() == 'a':
            add_client()
        elif answer.lower() == 'd':
            delete_client()
        elif answer.lower() == 'm':
            modify_client()    
        elif answer.lower() == 'v':
            print_all_clients()
        else:
            print("Invalid option selected.")

if __name__ == '__main__':
    main()


