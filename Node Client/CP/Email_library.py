# -*- coding: utf-8 -*-
import smtplib  

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage  

import os
import base64
import sys
from globals import config_obj, script_dir, logging

from PIL import Image

def setup():

    try:
        Email_config = config_obj["Email"]

        global sender, password, receiver, client_name, image_base64, subjects

        
        try:
            logo_file_path = os.path.join(script_dir, "templates", "logo.png")
            image = base64.b64encode(open(logo_file_path, "rb").read())
            image_base64 = image.decode() 
        except Exception as e:
            logging.warning("Error loading footer image: " + e)

        sender = Email_config["sender"]
        password = Email_config["password"]
        receiver = Email_config["receiver"]
        client_name = Email_config["client"]
        
        subjects = {key: Email_config[key].format(client_name=client_name) 
                for key in ['subject_U_M', 'subject_N_M', 'subject_image', 'subject_correlation']}
        
        logging.info("Correct Email setup")

    except Exception as e:
        logging.warning("Error during Email setup", e)
        sys.exit(1)

def load_template(template_file_path, Subject):
    """
    This function initializes a MIMEMultipart message object and sets the sender, recipient, and subject of the email.
    It also attaches the plain text body of the email.
    """
    # Create a new email message object
    message = MIMEMultipart()
    # Assign the sender email address
    message["From"] = sender
    # Assign the receiver email address
    message["To"] = receiver
    # Assign the subject of the email
    message["Subject"] = subjects[Subject]

    try:
        with open(template_file_path, "r", encoding="utf-8") as file:
            body = file.read()
        
    except Exception as e:
        logging.warning("Error loading template: " + e)

    return message, body


def send_email(message):
    try:
        server = smtplib.SMTP("smtp.office365.com", 587)
        server.starttls()
        server.login(sender, password)
        text = message.as_string()
        server.sendmail(sender, receiver, text)
        server.quit()
    except Exception as e:
        logging.warning("Error sending the email" + e)

def send_email_with_reading(sensor_name, sensor_type, unit, value, alarm_name):
    template_file_path = os.path.join(script_dir, "templates", "template_U_M.html")
    message, body = load_template(template_file_path)  
    # Format the body string with the actual values
    formatted_body = body.format(sensor_name = sensor_name, sensor_type = sensor_type, unit = unit, value = value, alarm_name = alarm_name, client_name = client_name, image_base64 = image_base64)
    
    # Add the formatted body to the email as HTML content
    message.attach(MIMEText(formatted_body, "html", "utf-8"))
    
    send_email(message)


def send_email_with_N_readings(sensor_name, sensor_type, unit, values, alarm_name):
    template_file_path = os.path.join(script_dir, "templates", "template_N_M.html")
    message, body = load_template(template_file_path)  
    
    # Prepare the rows for the table
    table_rows = ""
    for reading in values:
        table_rows += f"<tr><td>{reading.result}</td><td>{reading.unit}</td></tr>\n"
    
    # Format the body string with the actual values
    formatted_body = body.format(sensor_name = sensor_name, sensor_type = sensor_type, unit = unit, 
                                 table_rows = table_rows, N = len(values), alarm_name = alarm_name, 
                                 client_name = client_name, image_base64 = image_base64)
    
    # Add the formatted body to the email as HTML content
    message.attach(MIMEText(formatted_body, "html", "utf-8"))
    
    send_email(message)

def send_email_with_attachment(alarm_name, attachment_path, template_filename, subject):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_file_path = os.path.join(script_dir, "templates", template_filename)
    message, body = load_template(template_file_path, subject)

    with open(attachment_path, 'rb') as f:
        img_data = f.read()

    try:
        formatted_body = body.format(alarm_name=alarm_name, image_base64=image_base64)

        html_body = MIMEText(formatted_body, _subtype='html')
        message.attach(html_body)

        image = MIMEImage(img_data)
        image.add_header('Content-ID', '<image1>')
        message.attach(image)

        send_email(message)

    except Exception as e:
        print("Error loading footer image: " + str(e))