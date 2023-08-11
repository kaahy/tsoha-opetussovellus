from app import app
from flask import render_template, request, session, redirect
from sqlalchemy.sql import text
import re
from db import db
import users

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["name"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/")
        return render_template("error.html", message="Kirjautuminen ei onnistunut.")

@app.route("/logout")
def logout():
    # TODO: fix Internal Server Error when wasn't logged in
    del session["session_name"]
    del session["user_id"]
    del session["is_teacher"]
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        name = request.form["name"]
        password  = request.form["password1"]
        password2 = request.form["password2"]
        is_teacher = "f"
        if request.form["role"] == "teacher":
            is_teacher = "t"
        if not name or not password or not password2:
            return render_template("error.html", message="Et täyttänyt kaikkia kenttiä.")
        if password != password2:
            return render_template("error.html", message="Salasanat eivät täsmää.")
        if not re.search("^\S(.*\S)?$", name) or not re.search("^\S(.*\S)?$", password):
            # name or password can't start or end with a white space character
            return render_template("error.html", message="Valitsemasi nimi tai salasana ei kelpaa.")
        if users.register(name, password, is_teacher):
            users.login(name, password)
            return render_template("message.html", title="Tervetuloa", message="Tunnuksesi on luotu, " + name + ".")
        return render_template("error.html", message="Tunnuksen luominen ei onnistunut.")

@app.route("/courses")
def courses():
    sql = text("SELECT * FROM courses")
    result = db.session.execute(sql)
    course_list = result.fetchall()
    return render_template("courses.html", course_list=course_list)

@app.route("/course/<int:course_id>")
def course(course_id):
    sql = text("SELECT id, name, user_id FROM courses WHERE id=:course_id")
    result = db.session.execute(sql, {"course_id":course_id})
    course_info = result.fetchone()
    if not course_info:
        return render_template("error.html", message="Kurssia ei löydy.")
    pages = db.session.execute(text("SELECT id, title FROM course_pages WHERE course_id=:course_id ORDER BY id"), {"course_id":course_id}).fetchall()
    course_name = course_info.name
    teacher_id = course_info.user_id
    teacher_name = db.session.execute(text("SELECT name FROM users WHERE id=:id"), {"id":teacher_id}).fetchone()[0]
    course_id = course_info.id
    return render_template("course.html", pages=pages, course_name=course_name, course_id=course_id, teacher_name=teacher_name)

@app.route("/add_course", methods=["GET", "POST"])
def add_course():
    is_teacher = False
    if session.get("is_teacher"):
        if session["is_teacher"] == True:
            is_teacher = True
    if not is_teacher:
        return render_template("error.html", message="Et voi luoda kurssia, koska et ole kirjautunut opettajan tunnuksella.")
    if request.method == "GET":
        return render_template("add_course.html")
    if request.method == "POST":
        name = request.form["course_name"]
        user_id = session["user_id"]
        sql = text("INSERT INTO courses (name, user_id) VALUES (:name, :user_id) RETURNING id")
        result = db.session.execute(sql, {"name":name, "user_id":user_id})
        course_id = result.fetchone()[0]
        db.session.commit()
        return redirect("/course/" + str(course_id))

@app.route("/course_page/<int:course_page_id>")
def course_page(course_page_id):
    course_page = db.session.execute(text("SELECT id, course_id, title, content FROM course_pages WHERE id=:id"), {"id":course_page_id}).fetchone()
    if not course_page:
        return render_template("error.html", message="Sivua ei löydy.")
    course_name = db.session.execute(text("SELECT name FROM courses WHERE id=:id"), {"id":course_page.course_id}).fetchone().name
    return render_template("course_page.html", course_id=course_page.course_id, course_name=course_name, course_page_name=course_page.title, course_page_content=course_page.content, course_page_id=course_page_id)

@app.route("/course/<int:course_id>/add_page", methods=["GET", "POST"])
def add_course_page(course_id):
    course_creator_id = db.session.execute(text("SELECT user_id FROM courses WHERE id=:id"), {"id":course_id}).fetchone()[0]
    allow = False
    if session.get("user_id"):
        if session["user_id"] == course_creator_id:
            allow = True
    if not allow:
        return render_template("error.html", message="Et voi lisätä sivua tälle kurssille, koska et ole kirjautunut sen opettajana.")
    if request.method == "GET":
        course_name = db.session.execute(text("SELECT name FROM courses WHERE id=:id"), {"id":course_id}).fetchone()[0]
        return render_template("add_course_page.html", course_name=course_name, course_id=course_id)
    if request.method == "POST":
        try:
            title = request.form["title"]
            content = request.form["content"]
            db.session.execute(text("INSERT INTO course_pages (course_id, title, content) VALUES (:course_id, :title, :content)"), {"course_id":course_id, "title":title, "content":content})
            db.session.commit()
            return redirect(f"/course/{course_id}")
        except:
            return render_template("error.html", message="Sivun lisääminen ei onnistunut.")
        
@app.route("/course_page/<int:course_page_id>/edit", methods=["GET", "POST"])
def edit_course_page(course_page_id):
    course_id = db.session.execute(text("SELECT course_id FROM course_pages WHERE id=:id"), {"id":course_page_id}).fetchone()[0]
    course_creator_id = db.session.execute(text("SELECT user_id FROM courses WHERE id=:id"), {"id":course_id}).fetchone()[0]
    allow = False
    if session.get("user_id"):
        if session["user_id"] == course_creator_id:
            allow = True
    if not allow:
        return render_template("error.html", message="Et voi muokata tämän kurssin sivuja, koska et ole kirjautunut sen opettajana.")
    if request.method == "GET":
        course_page = db.session.execute(text("SELECT course_id, title, content FROM course_pages WHERE id=:id"), {"id":course_page_id}).fetchone()
        course_name = db.session.execute(text("SELECT name FROM courses WHERE id=:id"), {"id":course_page.course_id}).fetchone()[0]
        return render_template("edit_course_page.html", course_id=course_page.course_id, course_name=course_name, course_page_id=course_page_id, course_page_title=course_page.title, course_page_content=course_page.content)
    if request.method == "POST":
        try:
            title = request.form["title"]
            content = request.form["content"]
            db.session.execute(text("UPDATE course_pages SET title=:title, content=:content WHERE id=:id"), {"title":title, "content":content, "id":course_page_id})
            db.session.commit()
            return redirect(f"/course_page/{course_page_id}")
        except:
            return render_template("error.html", message="Sivun muokkaaminen ei onnistunut.")

# TODO: fix too much repeating code
