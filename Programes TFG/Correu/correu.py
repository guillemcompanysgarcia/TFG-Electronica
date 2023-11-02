import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

def send_email(sensor_name, sensor_type, date, result, unit, alarm_name, operation, threshold, client_name):
    # Your custom domain email and password
    email_address = "notificacions.SIMPQ@outlook.es"
    email_password = "musiSPiN"
    # Recipient email address
    to_email = "notificacions.SIMPQ@outlook.es"
    # Creating the email
    subject = "[Nova mesura de "+ client_name + " realitzada]"
   
    filename = "logo.png"
    image = base64.b64encode(open(filename, "rb").read())
    image_base64 = image.decode()   

    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h1 {{ color: #333; }}
            p {{ font-size: 14px; }}
            table.MsoNormalTable {{ 
                mso-style-name:"Taula normal";
                mso-tstyle-rowband-size:0;
                mso-tstyle-colband-size:0;
                mso-style-noshow:yes;
                mso-style-priority:99;
                mso-style-parent:"";
                mso-padding-alt:0cm 5.4pt 0cm 5.4pt;
                mso-para-margin:0cm;
                mso-pagination:widow-orphan;
                font-size:10.0pt;
                font-family:"Times New Roman",serif;
            }}
        </style>
    </head>
    <body>
        <h1>Nova mesura de {client_name} realitzada</h1>
        <p>
            El sensor <b>{sensor_name}</b>, de tipus <b>{sensor_type}</b>, ha realitzat una mesura a les <b>{date}</b> amb valor de <b>{result}{unit}</b>.
        </p>
        <p> 
            Aquest missatge ha estat enviat automàticament gràcies a l'alarma <b>{alarm_name}</b> de SIMPQ, que notifica a l'usuari si el valor del sensor <b>{sensor_name}</b> és <b>{operation}</b> a <b>{threshold} {unit}</b>.
        </p>
        <table>
    <tr>
        <td width="227" valign="bottom" style="width:6.0cm;padding:0cm 3.5pt 0cm 3.5pt;height:73.5pt">
        <p class="MsoNormal"><b><span style="color:#0070C0;">Chemplate Materials, S.L.</span></b></p>
        <p class="MsoNormal">C/ Empordà, 23</p>
        <p class="MsoNormal">P.I. Can Bernades-Subirà</p>
        <p class="MsoNormal">08130, Santa Perpètua de Mogoda</p>
        <p class="MsoNormal">(Barcelona) Spain</p>
        <p class="MsoNormal">T: +34 93 574 43 00</p>
        </td>
        <td width="286" style="width:214.75pt;padding:0cm 3.5pt 0cm 3.5pt;height:73.5pt">
        <p class="MsoNormal" align="center" style="text-align:center"><a href="http://www.chemplate.com/"><img border="0" width="277" height="52" src= "data:image/png;base64,{image_base64}" style="height:.541in;width:2.885in" alt="Resistec"></a><span><o:p></o:p></span></p>
        <p class="MsoNormal" align="center" style="text-align:center"><i><span style="color:#00B0F0;">We are Chemistry. We are Innovation.<o:p></o:p></span></i></p>
        <p class="MsoNormal"><a href="http://www.chemplate.com/"><span style="color:#0563C1;">http://www.chemplate.com</span></a><b><span><o:p></o:p></span></b></p>
        <p class="MsoNormal"><b><span><a href="https://chemplate.us3.list-manage.com/subscribe?u=bb561bf06d4c2b960bcd1bccb&amp;id=2aa79e5458&amp;e=&amp;c=01b5486011"><span style="color:#0563C1;">Join now</span></a></span></b><span> to our Newsletter !<o:p></o:p></span></p>
        </td>
    </tr>
</table>
    """

    msg = MIMEMultipart()
    msg["From"] = email_address
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    # Send the email using Outlook's SMTP server
    try:
        server = smtplib.SMTP("smtp.office365.com", 587)
        server.starttls()
        server.login(email_address, email_password)
        text = msg.as_string()
        server.sendmail(email_address, to_email, text)
        server.quit()
        print("Email successfully sent!")
    except Exception as e:
        print(f"Error occurred: {e}")

# Example usage
sensor_name = "Sensor 1"
sensor_type = "Temperatura"
date = "2023-04-09 12:00:00"
result = 25.5
unit = "°C"
alarm_name = "Alarma 1"
operation = "major que"
threshold = 20
client_name = "GDE"
send_email(sensor_name, sensor_type, date, result, unit, alarm_name, operation, threshold, client_name)
