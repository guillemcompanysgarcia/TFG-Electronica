import os
import sys

# Add the root directory to the Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)

from app import app, db, User,Role


def print_all_users():
    # Retrieve all users from the database
    users = User.query.all()

    for user in users:
        print(f"ID: {user.id}, Email: {user.email}, Username: {user.username}, Password Hash: {user.password_hash}, Roles: {[role.name for role in user.roles]}")

def add_user():
    email = input("Enter the email of the user: ") or 'admin@chemplate.com'
    password = input("Enter the password for the user: ") or 'admin'
    username = input("Enter the username for the user: ") or 'Admin'
    role_name = input("Enter the role for the user: ") or 'admin'

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print(f"A user with the email {email} already exists.")
        return

    role = Role.query.filter_by(name=role_name).first()
    if not role:
        role = Role(name=role_name)
        db.session.add(role)

    new_user = User(email=email, username=username)
    new_user.set_password(password)
    new_user.roles.append(role)

    db.session.add(new_user)
    db.session.commit()
    print("New user added successfully!")

def delete_user():
    email = input("Enter the email of the user to delete: ")
    user_to_delete = User.query.filter_by(email=email).first()
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        print(f"User {email} has been deleted.")
    else:
        print(f"No user found with email {email}.")

def modify_user():
    email = input("Enter the email of the user to modify: ")
    user_to_modify = User.query.filter_by(email=email).first()
    if user_to_modify:
        new_email = input(f"Enter the new email for the user (leave blank to keep '{user_to_modify.email}'): ")
        new_password = input(f"Enter the new password for the user (leave blank to keep the current one): ")
        new_username = input(f"Enter the new username for the user (leave blank to keep '{user_to_modify.username}'): ")
        new_role_name = input(f"Enter the new role for the user (leave blank to keep '{[role.name for role in user_to_modify.roles]}'): ")

        if new_email:
            user_to_modify.email = new_email
        if new_password:
            user_to_modify.set_password(new_password)
        if new_username:
            user_to_modify.username = new_username
        if new_role_name:
            new_role = Role.query.filter_by(name=new_role_name).first()
            if not new_role:
                new_role = Role(name=new_role_name)
                db.session.add(new_role)
            user_to_modify.roles.clear()
            user_to_modify.roles.append(new_role)

        db.session.commit()
        print(f"User {email} has been modified.")
    else:
        print(f"No user found with email {email}.")

def main():
    app.app_context().push()

    db.create_all()
    while 1:
        answer = input("Do you want to add a new user (a), delete a user (d), modify a user (m), or view all users (v)? ")

        if answer.lower() == 'a':
            add_user()
        elif answer.lower() == 'd':
            delete_user()
        elif answer.lower() == 'm':
            modify_user()
        elif answer.lower() == 'v':
            print_all_users()
        else:
            print("Invalid option selected.")

if __name__ == '__main__':
    main()