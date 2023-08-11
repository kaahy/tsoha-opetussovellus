from flask import session
from sqlalchemy.sql import text
from db import db

def login(username, password):
    sql = text("SELECT * FROM users WHERE name=:username AND password=:password")
    result = db.session.execute(sql, {"username":username, "password":password})
    user = result.fetchone()
    if not user:
        return False
    session["session_name"] = username
    session["user_id"] = user.id
    session["is_teacher"] = user.is_teacher
    return True

def register(name, password, is_teacher):
    try:
        sql = text("INSERT INTO users (name, password, is_teacher) VALUES (:name, :password, :is_teacher)")
        db.session.execute(sql, {"name":name, "password":password, "is_teacher":is_teacher})
        db.session.commit()
    except:
        return False
    return True
