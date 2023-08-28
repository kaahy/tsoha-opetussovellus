import secrets
from flask import session, request, abort
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
import courses

def login(username, password):
    sql = "SELECT id, password, is_teacher FROM users WHERE name=:username"
    row = db.session.execute(text(sql), {"username":username}).fetchone()
    if not row:
        return False
    if check_password_hash(row[1], password):
        session["session_name"] = username
        session["user_id"] = row.id
        session["is_teacher"] = row.is_teacher
        session["csrf_token"] = secrets.token_hex(16)
        return True
    return False

def logout():
    if session.get("session_name"):
        del session["session_name"]
    if session.get("user_id"):
        del session["user_id"]
    if "is_teacher" in session:
        del session["is_teacher"]

def register(name, password, is_teacher):
    try:
        password = generate_password_hash(password)
        sql = """INSERT INTO users (name, password, is_teacher)
                 VALUES (:name, :password, :is_teacher)"""
        db.session.execute(text(sql), {"name":name, "password":password, "is_teacher":is_teacher})
        db.session.commit()
    except:
        return False
    return True

def get_user_id():
    if session.get("user_id"):
        return session.get("user_id")
    return None

def is_allowed_to_edit_page(page_id):
    # this function tells if the user is logged in as the course creator
    page = courses.get_page(page_id)
    course_id = page["course_id"]
    course_creator_id = courses.get_course(course_id)["teacher_id"]
    if get_user_id() == course_creator_id:
        return True
    return False

def teacher_check(course_id):
    user_id = get_user_id()
    if not user_id:
        return False
    sql = f"SELECT COUNT(*) FROM courses WHERE id=:course_id and user_id={user_id}"
    if db.session.execute(text(sql), {"course_id":course_id}).fetchone()[0] > 0:
        return True
    return False

def get_name(user_id):
    sql = "SELECT name FROM users WHERE id=:id"
    return db.session.execute(text(sql), {"id":user_id}).fetchone()[0]

def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

def is_teacher(user_id):
    sql = "SELECT COUNT(*) FROM users WHERE id=:user_id AND is_teacher='t'"
    if db.session.execute(text(sql), {"user_id":user_id}).fetchone()[0]:
        return True
    return False
