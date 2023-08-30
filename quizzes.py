from sqlalchemy.sql import text
from db import db

def get_quizzes(page_id):
    sql = "SELECT id, page_id, question FROM quizzes WHERE page_id=:page_id"
    quizzes = db.session.execute(text(sql), {"page_id":page_id}).fetchall()
    choices = {}
    for quiz in quizzes:
        sql = f"SELECT id, content FROM choices WHERE quiz_id={quiz.id}"
        choices[quiz.id] = db.session.execute(text(sql)).fetchall()
    return {"quizzes": quizzes, "choices": choices}

def add_quiz(page_id, question, choices):
    if not question or len(choices) < 2:
        return False
    sql = "INSERT INTO quizzes (page_id, question) VALUES (:page_id, :question) RETURNING id"
    quiz_id = db.session.execute(text(sql), {"page_id":page_id, "question":question}).fetchone()[0]
    for choice in choices:
        content = choice["content"]
        is_correct = choice["is_correct"]
        sql = """INSERT INTO choices (quiz_id, content, is_correct)
                 VALUES (:quiz_id, :content, :is_correct)"""
        db.session.execute(text(sql), {"quiz_id":quiz_id, "content":content, "is_correct":is_correct})
    db.session.commit()
    return True

def delete_quiz(quiz_id):
    sql = "DELETE FROM quizzes WHERE id=:id"
    db.session.execute(text(sql), {"id":quiz_id})
    db.session.commit()

def move_quiz(quiz_id, page_id):
    sql = "UPDATE quizzes SET page_id=:page_id WHERE id=:quiz_id"
    db.session.execute(text(sql), {"quiz_id":quiz_id, "page_id":page_id})
    db.session.commit()

def save_results(page_id, user_id):
    # saves only correct results, at least for now
    sql = "SELECT id FROM quizzes WHERE page_id=:page_id"
    quiz_ids = db.session.execute(text(sql), {"page_id":page_id}).fetchall()
    quiz_ids = [quiz_ids[x][0] for x in range(len(quiz_ids))]
    for quiz_id in quiz_ids:
        if not is_quiz_solved(quiz_id, user_id):
            sql = f"INSERT INTO results (user_id, quiz_id, is_correct) VALUES (:user_id, '{quiz_id}', 't')"
            db.session.execute(text(sql), {"user_id":user_id})
            db.session.commit()

def is_quiz_solved(quiz_id, user_id):
    sql = """SELECT COUNT(*) FROM results
             WHERE quiz_id=:quiz_id AND user_id=:user_id AND is_correct='t'"""
    return db.session.execute(text(sql), {"quiz_id":quiz_id, "user_id":user_id}).fetchone()[0]

def check_quizzes(page_id, guesses):
    # student needs to answer correctly to all quizzes on the page
    sub = "(SELECT id FROM quizzes WHERE page_id=:page_id)"
    sql = "SELECT id FROM choices WHERE quiz_id IN " + sub + " AND is_correct='t'"
    correct_choices = db.session.execute(text(sql), {"page_id":page_id}).fetchall()
    correct_choices = [str(correct_choices[x][0]) for x in range(len(correct_choices))]
    return sorted(correct_choices) == sorted(guesses)

def get_quiz_ids(page_id):
    sql = "SELECT id FROM quizzes WHERE page_id=:page_id"
    ids = db.session.execute(text(sql), {"page_id":page_id}).fetchall()
    return [ids[x][0] for x in range(len(ids))]
