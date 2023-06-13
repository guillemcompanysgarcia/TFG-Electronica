import json
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_user import UserManager
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from dotenv import load_dotenv
import os
from models import Client, User, db, Role
from functools import wraps


# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Crea una instancia de la aplicación Flask
app = Flask(__name__)
app.app_context().push()

# Determine the absolute path of the database file
base_path = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(base_path, 'instance', 'database.db')

# Configura la base de datos principal
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Establece la clave secreta para la aplicación Flask
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Configura las opciones de Flask-User
app.config['USER_APP_NAME'] = 'SIMPQ'  # Nombre de la aplicación
app.config['USER_ENABLE_EMAIL'] = False  # Desactiva la funcionalidad de correo electrónico
app.config['USER_ENABLE_USERNAME'] = True  # Habilita la funcionalidad de nombre de usuario
app.config['USER_REQUIRE_RETYPE_PASSWORD'] = False  # Simplifica el proceso de registro

# Crea una instancia de UserManager y la configura con la aplicación Flask, la base de datos y el modelo de usuario
user_manager = UserManager(app, db, User, RoleClass=Role)



# Initialize the database outside the app context
with app.app_context():
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)

# Crea una instancia de LoginManager y la configura con la aplicación Flask


# Establece la vista de inicio de sesión para LoginManager
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.has_roles('admin'):
            flash('You need admin privileges to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('client_select'))
    else:
        return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = User.query.all()
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('Credencials incorrectes')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('client_select'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('logout.html')

@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
      if request.method == 'POST':
        field = request.form['field']
        value = request.form['value']
        
        user_id = current_user.id
        user = User.query.get(user_id)

        if user is not None:
          if field == 'username':
              user.username = value
          elif field == 'email':
              user.email = value
          elif field == 'password':
              user.set_password(value)

          db.session.commit()

      username = current_user.username
      email = current_user.email
      role = ', '.join(role.name for role in current_user.roles)
      return render_template('user.html', user={'username': username, 'email': email, 'role': role}, return_to_start = '/')

@app.route('/client_select', methods=['GET', 'POST'])
@login_required
def client_select():
    if request.method == 'POST':
        client_name = request.form['client']
        client = Client.query.filter_by(name=client_name).first()
        if client:
            return redirect(url_for('control_panel', client_name=client_name))

    clients = Client.query.all()
    return render_template('client_select.html', clients=clients)

@app.route('/control_panel/<string:client_name>', methods=['GET', 'POST'])
@login_required
def control_panel(client_name):
    client = Client.query.filter_by(name=client_name).first()
    if not current_user.has_role('admin'):
        return render_template('control_panel_no_privileges.html', client=client,
                               sensors_panel=client.sensors_panel,
                               data_base=client.data_base,
                               system_monitoring=client.system_monitoring)
    else:
        return render_template('control_panel.html', client=client,
                               sensors_panel=client.sensors_panel,
                               data_base=client.data_base,
                               system_monitoring=client.system_monitoring,
                               sensors_configuration='/control_panel/' + client_name + '/sensors_configuration',
                               actuators_configuration='/control_panel/' + client_name + '/actuators_configuration',
                               alarms_configuration='/control_panel/' + client_name + '/alarms_configuration')

@app.route('/control_panel/<string:client_name>/sensors_configuration', methods=['GET', 'POST'])
@login_required
@admin_required
def sensors_configuration(client_name):
    return_to_control_panel = '/control_panel/' + client_name
    sensors_data = read_configuration(client_name, 'sensors')
    actuators_link = return_to_control_panel + '/actuators_configuration'
    alarms_link = return_to_control_panel + '/alarms_configuration'

    return render_template(
        'sensors_configuration.html',
        data=sensors_data,
        return_to_control_panel=return_to_control_panel,
        actuators_link=actuators_link,
        alarms_link=alarms_link
    )

@app.route('/control_panel/<string:client_name>/actuators_configuration', methods=['GET', 'POST'])
@login_required
@admin_required
def actuators_configuration(client_name):
    return_to_control_panel = '/control_panel/' + client_name
    actuators_data = read_configuration(client_name, 'actuators')
    sensors_link = return_to_control_panel + '/sensors_configuration'
    alarms_link = return_to_control_panel + '/alarms_configuration'

    return render_template(
        'actuators_configuration.html',
        data=actuators_data,
        return_to_control_panel=return_to_control_panel,
        sensors_link=sensors_link,
        alarms_link=alarms_link
    )

@app.route('/control_panel/<string:client_name>/alarms_configuration', methods=['GET', 'POST'])
@login_required
@admin_required
def alarms_configuration(client_name):
    return_to_control_panel = '/control_panel/' + client_name
    alarms_data = read_configuration(client_name, 'alarms')
    sensors_link = return_to_control_panel + '/sensors_configuration'
    actuators_link = return_to_control_panel + '/actuators_configuration'

    return render_template(
        'alarms_configuration.html',
        data=alarms_data,
        return_to_control_panel=return_to_control_panel,
        sensors_link=sensors_link,
        actuators_link=actuators_link
    )
  

def read_configuration(client_name, config_type):
    try:
        config_path = os.path.join(base_path,'configurations', client_name, f"{config_type}_configuration.json")
        with open(config_path, encoding='UTF-8') as f:
            data = f.read()
            f.close()
        
        return data
        
    except:
        print(f"No {config_type} data from {client_name}")

@app.route('/download/<string:client_name>/<string:config_type>', methods=['POST'])
@login_required
def download(client_name, config_type):
    try:
            client = Client.query.filter_by(name=client_name).first()
            if client:
                table = request.get_data()
                config_path = os.path.join(base_path, 'configurations', client_name, f"{config_type}_configuration.json")
                with open(config_path, "w",encoding='UTF-8') as f:
                    f.write(table.decode('utf-8'))
                return ('/')
            else:
                print(f"{client_name} not found in the database.")
    except:
            print(f"Error writing {config_type} data to {client_name} {config_type} file.")


@app.route('/get_sensors_and_actuators/<client_name>')
@login_required
def get_sensors_and_actuators(client_name):

    data = read_configuration(client_name, "sensors")
    sensor_list = json.loads(data)
    sensors =[]
    for sensor in sensor_list:
        name = sensor["Nom del Sensor"]
        sensor_type = sensor["Tipus de Sensor"]
        sensor_unit = sensor["Unitat"]
        sensors.append(f"{name} ({sensor_type}) ({sensor_unit})")

    data = read_configuration(client_name, "actuators")
    actuator_list = json.loads(data)
    actuators =[]
    for actuator in actuator_list:
        name = actuator["Nom de l'Actuador"]
        actuator_type = actuator["Tipus d'Actuador"]
        actuators.append(f"{name} ({actuator_type})")
    return jsonify({'sensors': sensors, 'actuators': actuators})

@app.route('/get_sensors_interval/<client_name>/<string:sensor_name>')
@login_required
def get_sensors_interval(client_name, sensor_name):
    data = read_configuration(client_name, "sensors")
    sensors = json.loads(data)
    for sensor in sensors:
        if sensor['Nom del Sensor'] == sensor_name: 
            sensor_interval = sensor['Interval de Temps']
            return jsonify({'interval': sensor_interval})

    return jsonify({'error': 'Sensor not found'}), 404


if __name__ == '__main__':
    with app.app_context():
        app.run(host='0.0.0.0', port=80, debug=True)
