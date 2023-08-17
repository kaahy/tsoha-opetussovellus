from sqlalchemy.sql import text
from db import db

def get_courses():
    sql = "SELECT courses.id AS course_id, courses.name AS course_name, users.name AS teacher_name, (SELECT COUNT(DISTINCT user_id) FROM participants WHERE course_id=courses.id) AS participants_amount FROM courses, users WHERE courses.user_id=users.id"
    result = db.session.execute(text(sql))
    return result.fetchall()

def get_course(course_id):
    course = db.session.execute(text("SELECT id, name, user_id FROM courses WHERE id=:course_id"), {"course_id":course_id}).fetchone()
    if not course:
        return None
    name = course.name
    course_id = course.id
    teacher_id = course.user_id
    teacher_name = db.session.execute(text("SELECT name FROM users WHERE id=:id"), {"id":teacher_id}).fetchone()[0]
    pages = db.session.execute(text("SELECT id, title FROM course_pages WHERE course_id=:course_id ORDER BY id"), {"course_id":course_id}).fetchall()
    return {"id": course_id, "name":name, "pages":pages, "teacher_name":teacher_name, "teacher_id":teacher_id}

def get_course_page(course_page_id):
    page = db.session.execute(text("SELECT course_id, title, content FROM course_pages WHERE id=:id"), {"id":course_page_id}).fetchone()
    if not page:
        return None
    course_name = get_course(page.course_id)["name"]
    return {"title":page.title, "content":page.content, "course_name":course_name, "course_id":page.course_id}

def add_course(course_name, user_id):
    sql = text("INSERT INTO courses (name, user_id) VALUES (:name, :user_id) RETURNING id")
    result = db.session.execute(sql, {"name":course_name, "user_id":user_id})
    course_id = result.fetchone()[0]
    db.session.commit()
    return course_id

def add_course_page(course_id, title, content):
    db.session.execute(text("INSERT INTO course_pages (course_id, title, content) VALUES (:course_id, :title, :content)"), {"course_id":course_id, "title":title, "content":content})
    db.session.commit()

def edit_course_page(course_page_id, title, content):
    db.session.execute(text("UPDATE course_pages SET title=:title, content=:content WHERE id=:id"), {"title":title, "content":content, "id":course_page_id})
    db.session.commit()

def join(course_id, user_id):
    try:
        sql = f"INSERT INTO participants (course_id, user_id) VALUES ({course_id}, {user_id})"
        db.session.execute(text(sql))
        db.session.commit()
        return True
    except:
        return False
    
def is_participant(user_id, course_id):
    if not user_id:
        return False
    search = db.session.execute(text(f"SELECT * FROM participants WHERE user_id=:user_id AND course_id=:course_id"), {"user_id":user_id, "course_id":course_id}).fetchone()
    if search:
        return True
    return False
