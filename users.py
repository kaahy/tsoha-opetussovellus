from flask import session
from sqlalchemy.sql import text
from db import db
import courses
from werkzeug.security import check_password_hash, generate_password_hash

def login(username="", password=""):
    row = db.session.execute(text("SELECT id, password, is_teacher FROM users WHERE name=:username"), {"username":username}).fetchone()
    if not row:
        return False
    if check_password_hash(row[1], password):
        session["session_name"] = username
        session["user_id"] = row.id
        session["is_teacher"] = row.is_teacher
        return True
    return False

def register(name, password, is_teacher):
    try:
        password = generate_password_hash(password)
        sql = text("INSERT INTO users (name, password, is_teacher) VALUES (:name, :password, :is_teacher)")
        db.session.execute(sql, {"name":name, "password":password, "is_teacher":is_teacher})
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
    page = courses.get_course_page(page_id)
    course_id = page["course_id"]
    course_creator_id = courses.get_course(course_id)["teacher_id"]
    if get_user_id() == course_creator_id:
        return True
    return False

def teacher_check(course_id):
    user_id = get_user_id()
    if not user_id:
        return False
    sql = f"SELECT COUNT(*) FROM courses WHERE id={course_id} and user_id={user_id}"
    if db.session.execute(text(sql)).fetchone()[0] > 0:
        return True
    return False
