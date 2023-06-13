from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_user import UserMixin


db = SQLAlchemy()


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)


roles_users = db.Table('roles_users',
    db.Column('User_id', db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE')),
    db.Column('Role_id', db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))
)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False, server_default='')
    username = db.Column(db.String(120), unique=True, nullable=False)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    @property
    def password(self):
        return self.password_hash
    def __repr__(self):
        return self.username
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

class Client(db.Model):
    __tablename__ = 'client'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    sensors_panel = db.Column(db.String(100), nullable=False)
    data_base = db.Column(db.String(100), nullable=False)
    system_monitoring = db.Column(db.String(100), nullable=False)
    def __repr__(self):
        return self.name