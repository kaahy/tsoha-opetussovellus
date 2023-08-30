import re
from flask import render_template, request, session, redirect
from app import app
import users
import courses
import quizzes
import forms

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
    users.logout()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", name_min=forms.get_min("name"), name_max=forms.get_max("name"), password_min=forms.get_min("password"), password_max=forms.get_max("password"))
    if request.method == "POST":
        name = request.form["name"].strip()
        password  = request.form["password1"]
        password2 = request.form["password2"]
        is_teacher = "f"
        if request.form["role"] == "teacher":
            is_teacher = "t"
        if not name or not password or not password2:
            return render_template("error.html", message="Et täyttänyt kaikkia kenttiä.")
        if not forms.check_length(name, "name") or not forms.check_length(password, "password"):
            return render_template("error.html", message="Nimen tai salasanan pituus ei kelpaa.")
        if password != password2:
            return render_template("error.html", message="Salasanat eivät täsmää.") 
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
    return render_template("course.html", course_info=course, pages=course["pages"], participant=is_participant)

@app.route("/add_course", methods=["GET", "POST"])
def add_course():
    if not users.is_teacher(users.get_user_id()):
        return render_template("error.html", message="Et voi luoda kurssia, koska et ole kirjautunut opettajan tunnuksella.")
    if request.method == "GET":
        return render_template("add_course.html", min=forms.get_min("course name"), max=forms.get_max("course name"))
    if request.method == "POST":
        course_name = request.form["course_name"]
        if not forms.check_length(course_name, "course name"):
            return render_template("error.html", message="Syötit liikaa tai liian vähän tekstiä.")
        users.check_csrf()
        new_course_id = courses.add_course(course_name, session["user_id"])
        if new_course_id:
            return redirect("/course/" + str(new_course_id))

@app.route("/page/<int:page_id>", methods=["GET", "POST"])
def show_page(page_id):
    page = courses.get_page(page_id)
    if not page:
        return render_template("error.html", message="Sivua ei löydy.")
    if request.method == "GET":
        quizzes_info = quizzes.get_quizzes(page_id)
        return render_template("page.html", course_id=page["course_id"], course_name=page["course_name"], page_name=page["title"], page_content=page["content"], page_id=page_id, quizzes=quizzes_info["quizzes"], choices=quizzes_info["choices"])
    if request.method == "POST":
        user_id = users.get_user_id()
        if not user_id: # TODO: course participant check
            return render_template("error.html", message="Et ole kirjautunut.")
        users.check_csrf()
        guesses = request.form.getlist("guesses")
        if quizzes.check_quizzes(page_id, guesses):
            quizzes.save_results(page_id, user_id)
            return render_template("message.html", title="Tulos", message="Sait kaikki oikein!")
        return render_template("message.html", title="Tulos", message="Et saanut kaikkia oikein.")

@app.route("/course/<int:course_id>/add_page", methods=["GET", "POST"])
def add_page(course_id):
    if not users.teacher_check(course_id):
        return render_template("error.html", message="Et voi lisätä sivua tälle kurssille, koska et ole kirjautunut sen opettajana.")
    if request.method == "GET":
        course_name = courses.get_course(course_id)["name"]
        return render_template("add_page.html", course_name=course_name, course_id=course_id, title_min=forms.get_min("page title"), title_max=forms.get_max("page title"), content_min=forms.get_min("page content"), content_max=forms.get_max("page content"))
    if request.method == "POST":
        users.check_csrf()
        page_title = request.form["title"]
        page_content = request.form["content"]
        if not forms.check_length(page_title, "page title"):
            return render_template("error.html", message="Syötit liikaa tai liian vähän tekstiä.")
        courses.add_page(course_id, page_title, page_content)
        return redirect(f"/course/{course_id}")

@app.route("/page/<int:page_id>/edit", methods=["GET", "POST"])
def edit_page(page_id):
    if not users.is_allowed_to_edit_page(page_id):
        return render_template("error.html", message="Et voi muokata tämän kurssin sivuja, koska et ole kirjautunut sen opettajana.")
    if request.method == "GET":
        page = courses.get_page(page_id)
        course_id = page["course_id"]
        course_name = courses.get_course(course_id)["name"]
        return render_template("edit_page.html", course_id=course_id, course_name=course_name, page_id=page_id, page_title=page["title"], page_content=page["content"], title_min=forms.get_min("page title"), title_max=forms.get_max("page title"), content_min=forms.get_min("page content"), content_max=forms.get_max("page content"))
    if request.method == "POST":
        users.check_csrf()
        if not forms.check_length(request.form["title"], "page title"):
            return render_template("error.html", message="Syötit liikaa tai liian vähän tekstiä.")
        courses.edit_page(page_id, request.form["title"], request.form["content"])
        return redirect(f"/page/{page_id}")

@app.route("/page/<int:page_id>/add_quiz", methods=["GET", "POST"])
def add_quiz(page_id):
    if not users.is_allowed_to_edit_page(page_id):
        return render_template("error.html", message="Vain kurssin opettaja voi lisätä tehtäviä.")
    if request.method == "GET":
        return render_template("add_quiz.html", page_id=page_id, choice_min=forms.get_min("choice"), choice_max=forms.get_max("choice"),  question_min=forms.get_min("question"), question_max=forms.get_max("question"))
    if request.method == "POST":
        users.check_csrf()
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
        if quizzes.add_quiz(page_id, request.form["question"], choices):
            return redirect(f"/page/{page_id}")
        return render_template("error.html", message="Tehtävän lisääminen ei onnistunut. Syötithän kysymyksen ja ainakin kaksi vaihtoehtoa?")

@app.route("/course/<int:course_id>/join", methods=["GET", "POST"])
def join_course(course_id):
    if request.method == "GET":
        return render_template("join_course.html", course=courses.get_course(course_id))
    if request.method == "POST":
        users.check_csrf()
        if courses.join(course_id, users.get_user_id()):
            return course_starting_page(course_id)
        return render_template("error.html", message="Kurssille liittyminen ei onnistunut.")

@app.route("/course/<int:course_id>/leave", methods=["GET", "POST"])
def leave_course(course_id):
    if request.method == "GET":
        return render_template("leave_course.html", course=courses.get_course(course_id))
    if request.method == "POST":
        users.check_csrf()
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
        return render_template("user_course_statistics.html", statistics=statistics, course=course_info, course_points=course_points, student_name=student_name, student_id=user_id)

@app.route("/page/<int:page_id>/delete", methods=["GET", "POST"])
def delete_page(page_id):
    course_id = courses.get_course_id_by_page_id(page_id)
    if not users.teacher_check(course_id):
        return render_template("error.html", message="Toiminto on vain kurssin opettajalle.")
    if request.method == "GET":
        return render_template("delete_page.html", page_id=page_id)
    if request.method == "POST":
        users.check_csrf()
        courses.delete_page(page_id)
        return redirect(f"/course/{course_id}")

@app.route("/course/<int:course_id>/delete", methods=["GET", "POST"])
def delete_course(course_id):
    if not users.teacher_check(course_id):
        return render_template("error.html", message="Toiminto on vain kurssin opettajalle.")
    if request.method == "GET":
        course_name = courses.get_course_name(course_id)
        return render_template("delete_course.html", course_id=course_id, course_name=course_name)
    if request.method == "POST":
        users.check_csrf()
        courses.delete_course(course_id)
        return redirect("/courses")

@app.route("/profile/<int:user_id>")
def profile(user_id):
    if not users.exists(user_id):
        return render_template("message.html", message="Käyttäjää ei löydy.")
    joined_courses = courses.get_joined_courses(user_id)
    teached_courses = courses.get_teached_courses(user_id)
    name = users.get_name(user_id)
    is_teacher = users.is_teacher(user_id)
    return render_template("profile.html", user_id=user_id, is_teacher=is_teacher, name=name, joined_courses=joined_courses, teached_courses=teached_courses)

@app.route("/page/<int:page_id>/edit_quizzes", methods=["GET", "POST"])
def edit_quizzes(page_id):
    if not users.is_allowed_to_edit_page(page_id):
        return render_template("error.html", message="Toiminto on vain kurssin opettajalle.")
    if request.method == "GET":
        return render_template("edit_quizzes.html", page_id=page_id, quizzes=quizzes.get_quizzes(page_id)["quizzes"], pages=courses.get_pages(courses.get_course_id_by_page_id(page_id)))
    if request.method == "POST":
        quiz_id = request.form["quiz_id"]
        if int(quiz_id) not in quizzes.get_quiz_ids(page_id):
            return render_template("error.html", message="Toiminto ei onnistu.")
        users.check_csrf()
        if request.form["action"] == "delete":
            quizzes.delete_quiz(quiz_id)
            return redirect(f"/page/{page_id}")
        if request.form["action"] == "move":
            new_page_id = request.form["page_id"]
            if not users.is_allowed_to_edit_page(new_page_id):
                return render_template("error.html", message="Toiminto on vain kurssin opettajalle.")
            quizzes.move_quiz(quiz_id, new_page_id)
            return redirect(f"/page/{new_page_id}")

@app.route("/delete", methods=["GET", "POST"])
def delete_user():
    if request.method == "GET":
        return render_template("delete_user.html")
    if request.method == "POST":
        users.check_csrf()
        user_id = int(request.form["user_id"])
        if not "confirm_user_deletion" in request.form:
            return redirect(f"/profile/{user_id}")
        if user_id == users.get_user_id():
            users.delete(user_id)
            logout()
            return redirect("/")
        return render_template("error.html", message="Et ole kirjautunut tunnuksella, jota yrität poistaa.")
