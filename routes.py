from app import app
from flask import render_template, request, session, redirect
import re
import users
import courses
import quizzes

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
    is_participant = courses.is_participant(users.get_user_id(), course_id)
    if not course:
        return render_template("error.html", message="Kurssia ei löydy.")
    return render_template("course.html", pages=course["pages"], course_name=course["name"], course_id=course["id"], teacher_name=course["teacher_name"], participant=is_participant)

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
        quizzes_info = quizzes.get_quizzes(course_page_id)
        return render_template("course_page.html", course_id=page["course_id"], course_name=page["course_name"], course_page_name=page["title"], course_page_content=page["content"], course_page_id=course_page_id, quizzes=quizzes_info["quizzes"], choices=quizzes_info["choices"])
    if request.method == "POST":
        user_id = users.get_user_id()
        if not user_id: # TODO: course participant check
            return render_template("error.html", message="Et ole kirjautunut.")
        guesses = request.form.getlist("guesses")
        if quizzes.check_quizzes(course_page_id, guesses):
            quizzes.save_results(course_page_id, user_id)
            return render_template("message.html", title="Tulos", message="Sait kaikki oikein!")
        return render_template("message.html", title="Tulos", message="Et saanut kaikkia oikein.")

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
        if quizzes.add_quiz(course_page_id, request.form["question"], choices):
            return redirect(f"/course_page/{course_page_id}")
        return render_template("error.html", message="Tehtävän lisääminen ei onnistunut. Syötithän kysymyksen ja ainakin kaksi vaihtoehtoa?")
    
@app.route("/course/<int:course_id>/join", methods=["GET", "POST"])
def join_course(course_id):
    if request.method == "GET":
        return render_template("join_course.html", course=courses.get_course(course_id))
    if request.method == "POST":
        if courses.join(course_id, users.get_user_id()):
            return course_starting_page(course_id)
        return render_template("error.html", message="Kurssille liittyminen ei onnistunut.")

@app.route("/course/<int:course_id>/leave", methods=["GET", "POST"])
def leave_course(course_id):
    if request.method == "GET":
        return render_template("leave_course.html", course=courses.get_course(course_id))
    if request.method == "POST":
        if courses.leave(course_id, users.get_user_id()):
            return course_starting_page(course_id)
        return render_template("error.html", message="Toiminto ei onnistunut.")

@app.route("/course/<int:course_id>/participants")
def participants(course_id):
    if users.teacher_check(course_id):
        return render_template("participants.html", participants=courses.get_participants(course_id))
    return render_template("error.html", message="Vain kurssin opettaja voi nähdä sivun.")

@app.route("/course/<int:course_id>/statistics")
def course_statistics(course_id):
    if users.teacher_check(course_id):
        statistics = courses.get_course_points(course_id)
        if not statistics:
            return render_template("message.html", message="Kurssia tai tilastoja ei löydy.")
        return render_template("statistics.html", statistics=statistics, max_points=courses.get_course_max_points(course_id), course_id=course_id, course_name=courses.get_course_name(course_id))
    return render_template("error.html", message="Vain kurssin opettaja voi nähdä sivun.")

@app.route("/course/<int:course_id>/statistics/user/<int:user_id>")
def user_course_statistics(course_id, user_id):
    allow = False
    if users.teacher_check(course_id) or users.get_user_id() == user_id:
        allow = True
    if not allow:
        return render_template("error.html", message="Sinulla ei ole oikeuksia sisältöön.")
    if allow:
        statistics = courses.get_user_course_statistics(user_id, course_id)
        course_points = courses.get_users_course_points(user_id, course_id)
        student_name = users.get_name(user_id)
        course_info = courses.get_course(course_id)
        return render_template("user_course_statistics.html", statistics=statistics, course=course_info, course_points=course_points, student_name=student_name)

@app.route("/course_page/<int:page_id>/delete", methods=["GET", "POST"])
def delete(page_id):
    course_id = courses.get_course_id_by_page_id(page_id)
    if not users.teacher_check(course_id):
        return render_template("error.html", message="Toiminto on vain kurssin opettajalle.")
    if request.method == "GET":
        return render_template("delete_page.html", page_id=page_id)
    if request.method == "POST":
        if request.form["csrf_token"] != session["csrf_token"]:
            return render_template("error.html", message="Sivun poistaminen ei onnistunut.")
        courses.delete_page(page_id)
        return redirect(f"/course/{course_id}")
