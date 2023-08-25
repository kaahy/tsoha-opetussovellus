from sqlalchemy.sql import text
from db import db
import quizzes

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
    pages = db.session.execute(text("SELECT id, title FROM pages WHERE course_id=:course_id ORDER BY id"), {"course_id":course_id}).fetchall()
    max_points = get_course_max_points(course_id)
    return {"id": course_id, "name":name, "pages":pages, "teacher_name":teacher_name, "teacher_id":teacher_id, "max_points":max_points}

def get_page(page_id):
    page = db.session.execute(text("SELECT course_id, title, content FROM pages WHERE id=:id"), {"id":page_id}).fetchone()
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

def add_page(course_id, title, content):
    db.session.execute(text("INSERT INTO pages (course_id, title, content) VALUES (:course_id, :title, :content)"), {"course_id":course_id, "title":title, "content":content})
    db.session.commit()

def edit_page(page_id, title, content):
    db.session.execute(text("UPDATE pages SET title=:title, content=:content WHERE id=:id"), {"title":title, "content":content, "id":page_id})
    db.session.commit()

def join(course_id, user_id):
    try:
        sql = "INSERT INTO participants (course_id, user_id) VALUES (:course_id, :user_id)"
        db.session.execute(text(sql), {"course_id":course_id, "user_id":user_id})
        db.session.commit()
        return True
    except:
        return False

def leave(course_id, user_id):
    try:
        sql = "DELETE FROM participants WHERE course_id=:course_id AND user_id=:user_id"
        db.session.execute(text(sql), {"course_id":course_id, "user_id":user_id})
        db.session.commit()
    except:
        return False
    return True

def is_participant(user_id, course_id):
    if not user_id:
        return False
    search = db.session.execute(text("SELECT * FROM participants WHERE user_id=:user_id AND course_id=:course_id"), {"user_id":user_id, "course_id":course_id}).fetchone()
    if search:
        return True
    return False

def get_participants(course_id):
    sql = "SELECT participants.user_id AS id, users.name FROM participants, users WHERE course_id=:course_id AND participants.user_id=users.id"
    return db.session.execute(text(sql), {"course_id":course_id}).fetchall()

def get_course_max_points(course_id):
    sql = "SELECT COUNT(*) FROM quizzes WHERE page_id IN (SELECT id FROM pages WHERE course_id=:course_id)"
    return db.session.execute(text(sql), {"course_id":course_id}).fetchone()[0]

def get_course_points(course_id):
    page_ids = "SELECT id FROM pages WHERE course_id=:course_id" # pages in the course
    quiz_ids = "SELECT id FROM quizzes WHERE page_id IN (" + page_ids + ")" # quizzes in pages
    sub = "SELECT COUNT(DISTINCT quiz_id) FROM results WHERE is_correct='t' AND user_id=participants.user_id AND quiz_id IN (" + quiz_ids + ")"
    sql = "SELECT participants.user_id as id, users.name, (" + sub + ") AS points FROM participants, users WHERE participants.user_id=users.id AND course_id=:course_id"
    return db.session.execute(text(sql), {"course_id":course_id}).fetchall() # all participants' course points (id, name, points)

def get_users_course_points(user_id, course_id):
    # return one user's course points
    page_ids = "SELECT id FROM pages WHERE course_id=:course_id"
    quiz_ids = "SELECT id FROM quizzes WHERE page_id IN (" + page_ids + ")"
    sql = "SELECT COUNT(DISTINCT quiz_id) FROM results WHERE is_correct='t' AND user_id=:user_id AND quiz_id IN (" + quiz_ids + ")"
    return db.session.execute(text(sql), {"course_id":course_id, "user_id":user_id}).fetchone()[0]

def get_users_page_points(user_id, page_id):
    # return one user's page points
    sub = "SELECT id FROM quizzes WHERE page_id=:page_id"
    sql = "SELECT COUNT(DISTINCT quiz_id) FROM results WHERE is_correct='t' AND user_id=:user_id AND quiz_id IN (" + sub + ")"
    return db.session.execute(text(sql), {"user_id":user_id, "page_id":page_id}).fetchone()[0]

def get_page_max_points(page_id):
    return db.session.execute(text("SELECT COUNT(*) FROM quizzes WHERE page_id=:page_id"), {"page_id":page_id}).fetchone()[0]

def get_course_name(course_id):
    sql = "SELECT name FROM courses WHERE id=:course_id"
    return db.session.execute(text(sql), {"course_id":course_id}).fetchone()[0]

def get_course_id_by_page_id(page_id):
    sql = "SELECT course_id FROM pages WHERE id=:id"
    course_id = db.session.execute(text(sql), {"id":page_id}).fetchone()[0]
    if not course_id:
        return None
    return course_id

def delete_page(page_id):
    sql = "DELETE FROM pages WHERE id=:id"
    db.session.execute(text(sql), {"id":page_id})
    db.session.commit()

def delete_course(course_id):
    sql = "DELETE FROM courses WHERE id=:id"
    db.session.execute(text(sql), {"id":course_id})
    db.session.commit()

def get_user_course_statistics(user_id, course_id):
    result = []
    pages = db.session.execute(text("SELECT id, title FROM pages WHERE course_id=:course_id"), {"course_id":course_id}).fetchall()
    for page in pages:
        quiz_list = []
        quiz_ids = quizzes.get_quiz_ids(page.id)
        for quiz_id in quiz_ids:
            question = db.session.execute(text(f"SELECT question FROM quizzes WHERE id={quiz_id}")).fetchone()[0]
            quiz_list.append({"quiz_id": quiz_id, "question": question, "is_correct": quizzes.is_quiz_solved(quiz_id, user_id)})
        result.append({"page_id": page.id, "page_title": get_page_title(page.id), "page_points": get_users_page_points(user_id, page.id), "page_max_points": get_page_max_points(page.id), "quizzes": quiz_list})
    return result

def get_page_title(page_id):
    sql = "SELECT title FROM pages WHERE id=:page_id"
    return db.session.execute(text(sql), {"page_id":page_id}).fetchone()[0]
