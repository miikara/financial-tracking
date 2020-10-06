from db import db
from werkzeug.security import generate_password_hash

def add_user(username,first_name,last_name,email,password):
    hash_value = generate_password_hash(password)
    sql = "INSERT INTO users (username, first_name, last_name, email, password, registration_time) VALUES (:username,:first_name,:last_name,:email,:password, NOW())"    
    db.session.execute(sql, {"username":username,"first_name":first_name,"last_name":last_name,"password":hash_value,"email":email})
    db.session.commit()
    return True

def username_exists(username):
    sql = "SELECT username FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    try:
        db_username = result.fetchone()[0]
    except:
        db_username = None
    if username == db_username:
        return True
    else:
        return False

def get_user_id(username):
    sql = "SELECT user_id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    try:
        user_id = result.fetchone()[0]
    except:
        user_id = None
    return user_id

def get_password(username):
    sql = "SELECT password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    try:
        password = result.fetchone()[0]
    except:
        password = None
    return password

def update_password(username,new_password):
    return True

