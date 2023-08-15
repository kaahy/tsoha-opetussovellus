from app import app
from flask import render_template, request, session, redirect
import re
import users
import courses

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
def courses_page():
    course_list = courses.get_courses()
    return render_template("courses.html", course_list=course_list)

@app.route("/course/<int:course_id>")
def course_starting_page(course_id):
    course = courses.get_course(course_id)
    if not course:
        return render_template("error.html", message="Kurssia ei löydy.")
    return render_template("course.html", pages=course["pages"], course_name=course["name"], course_id=course["id"], teacher_name=course["teacher_name"])

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
        new_course_id = courses.add_course(request.form["course_name"], session["user_id"])
        if new_course_id:
            return redirect("/course/" + str(new_course_id))

@app.route("/course_page/<int:course_page_id>", methods=["GET", "POST"])
def course_page(course_page_id):
    page = courses.get_course_page(course_page_id)
    if not page:
        return render_template("error.html", message="Sivua ei löydy.")
    if request.method == "GET":
        quizzes = courses.get_quizzes(course_page_id)
        return render_template("course_page.html", course_id=page["course_id"], course_name=page["course_name"], course_page_name=page["title"], course_page_content=page["content"], course_page_id=course_page_id, quizzes=quizzes["quizzes"], choices=quizzes["choices"])
    if request.method == "POST":
        return render_template("error.html", message="Tehtävien tarkastus ei toimi vielä.")

@app.route("/course/<int:course_id>/add_page", methods=["GET", "POST"])
def add_course_page(course_id):
    course_creator_id = courses.get_course(course_id)["teacher_id"]
    allow = False
    if session.get("user_id"):
        if session["user_id"] == course_creator_id:
            allow = True
    if not allow:
        return render_template("error.html", message="Et voi lisätä sivua tälle kurssille, koska et ole kirjautunut sen opettajana.")
    if request.method == "GET":
        course_name = courses.get_course(course_id)["name"]
        return render_template("add_course_page.html", course_name=course_name, course_id=course_id)
    if request.method == "POST":
        courses.add_course_page(course_id, request.form["title"], request.form["content"])
        return redirect(f"/course/{course_id}")
        
@app.route("/course_page/<int:course_page_id>/edit", methods=["GET", "POST"])
def edit_course_page(course_page_id):
    page = courses.get_course_page(course_page_id)
    course_id = page["course_id"]
    course_creator_id = courses.get_course(course_id)["teacher_id"]
    allow = False
    if session.get("user_id"):
        if session["user_id"] == course_creator_id:
            allow = True
    if not allow:
        return render_template("error.html", message="Et voi muokata tämän kurssin sivuja, koska et ole kirjautunut sen opettajana.")
    if request.method == "GET":
        course_name = courses.get_course(course_id)["name"]
        return render_template("edit_course_page.html", course_id=course_id, course_name=course_name, course_page_id=course_page_id, course_page_title=page["title"], course_page_content=page["content"])
    if request.method == "POST":
        courses.edit_course_page(course_page_id, request.form["title"], request.form["content"])
        return redirect(f"/course_page/{course_page_id}")

@app.route("/course_page/<int:course_page_id>/add_quiz", methods=["GET", "POST"])
def add_quiz(course_page_id):
    if not users.is_allowed_to_edit_page(course_page_id):
        return render_template("error.html", message="Vain kurssin opettaja voi lisätä tehtäviä.")
    if request.method == "GET":
        return render_template("add_quiz.html", page_id=course_page_id)
    if request.method == "POST":
        correct_choice_numbers = request.form.getlist("correct_choices")
        choices = []
        for field in request.form:
            choice_number = re.search("^choice_([0-9]+)$", field)
            if choice_number:
                choice_number = choice_number[1]
                content = request.form[field]
                if content:
                    is_correct = "f"
                    if choice_number in correct_choice_numbers:
                        is_correct = "t"
                    choices.append({"content": content, "is_correct":is_correct})
        if courses.add_quiz(course_page_id, request.form["question"], choices):
            return redirect(f"/course_page/{course_page_id}")
        return render_template("error.html", message="Tehtävän lisääminen ei onnistunut. Syötithän kysymyksen ja ainakin kaksi vaihtoehtoa?")