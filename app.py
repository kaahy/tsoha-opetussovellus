from flask import Flask
from flask import render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from os import getenv

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

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
        sql = text("SELECT * FROM users WHERE name=:username AND password=:password")
        result = db.session.execute(sql, {"username":username, "password":password})
        user = result.fetchone()
        if not user:
            return render_template("error.html", message="Väärä nimi tai salasana.")
        session["session_name"] = username
        return redirect("/")
        # TODO: better password security
    
@app.route("/logout")
def logout():
    # TODO: fix Internal Server Error when wasn't logged in
    del session["session_name"]
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
    if password != password2:
        return render_template("error.html", message="Salasanat eivät täsmää.")
    try:
        sql = text("INSERT INTO users (name, password, is_teacher) VALUES (:name, :password, :is_teacher)")
        db.session.execute(sql, {"name":name, "password":password, "is_teacher":is_teacher})
        db.session.commit()
    except:
        return render_template("error.html", message="Tunnuksen luominen ei onnistunut.")
    return render_template("message.html", title="Tervetuloa", message="Tunnuksesi on luotu, " + name + ". Voit nyt kirjautua sisään.")
    
@app.route("/courses")
def courses():
    sql = text("SELECT * FROM courses")
    result = db.session.execute(sql)
    course_list = result.fetchall()
    message = ""
    if not course_list:
        message = "<p>Kursseja ei vielä ole.</p>"
    return render_template("courses.html", message=message, course_list=course_list)
    
@app.route("/course/<int:course_id>")
def course(course_id):
    sql = text("SELECT * FROM courses WHERE id=:course_id")
    result = db.session.execute(sql, {"course_id":course_id})
    course_info = result.fetchone()
    if not course_info:
        return render_template("error.html", message="Kurssia ei löydy.")
    return render_template("course.html", course_info=course_info)
