from flask import Flask
from flask import render_template
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

@app.route("/login")
def login():
    return render_template("login.html")
    
@app.route("/register")
def register():
    return render_template("register.html")
    
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
