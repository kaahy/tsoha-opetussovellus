from sqlalchemy.sql import text
from db import db

def get_quizzes(course_page_id):
    quizzes = db.session.execute(text("SELECT id, course_page_id, question FROM quizzes WHERE course_page_id=:course_page_id"), {"course_page_id":course_page_id}).fetchall()
    choices = {}
    for quiz in quizzes:
        choices[quiz.id] = db.session.execute(text(f"SELECT id, content FROM choices WHERE quiz_id={quiz.id}")).fetchall()
    return {"quizzes": quizzes, "choices": choices}

def add_quiz(course_page_id, question, choices):
    if not question or len(choices) < 2:
        return False
    quiz_id = db.session.execute(text("INSERT INTO quizzes (course_page_id, question) VALUES (:course_page_id, :question) RETURNING id"), {"course_page_id":course_page_id, "question":question}).fetchone()[0]
    for choice in choices:
        content = choice["content"]
        is_correct = choice["is_correct"]
        db.session.execute(text("INSERT INTO choices (quiz_id, content, is_correct) VALUES (:quiz_id, :content, :is_correct)"), {"quiz_id":quiz_id, "content":content, "is_correct":is_correct})   
    db.session.commit()
    return True

def save_results(page_id, user_id):
    # saves only correct results, at least for now
    quiz_ids = db.session.execute(text(f"SELECT id FROM quizzes WHERE course_page_id={page_id}")).fetchall()
    quiz_ids = [quiz_ids[x][0] for x in range(len(quiz_ids))]
    for quiz_id in quiz_ids:
        if not is_quiz_solved(quiz_id, user_id):
            db.session.execute(text(f"INSERT INTO results (user_id, quiz_id, is_correct) VALUES ('{user_id}', '{quiz_id}', 't')"))
            db.session.commit()

def is_quiz_solved(quiz_id, user_id):
    sql = f"SELECT COUNT(*) FROM results WHERE quiz_id={quiz_id} AND user_id={user_id} AND is_correct='t'"
    if db.session.execute(text(sql)).fetchone()[0]:
        return True
    return False

def check_quizzes(page_id, guesses):
    # student needs to answer correctly to all quizzes on the page
    correct_choices = db.session.execute(text("SELECT id FROM choices WHERE quiz_id IN (SELECT id FROM quizzes WHERE course_page_id=:page_id) AND is_correct='t'"), {"page_id":page_id}).fetchall()
    correct_choices = [str(correct_choices[x][0]) for x in range(len(correct_choices))]
    if sorted(correct_choices) == sorted(guesses):
        return True
    return False
