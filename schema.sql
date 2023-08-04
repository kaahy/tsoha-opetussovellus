CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	name TEXT UNIQUE,
	password TEXT,
	is_teacher BOOLEAN
);

CREATE TABLE courses (
	id SERIAL PRIMARY KEY,
	name TEXT,
	user_id INTEGER REFERENCES users
);

CREATE TABLE course_pages (
	id SERIAL PRIMARY KEY,
	course_id INTEGER REFERENCES courses,
	title TEXT,
	content TEXT
);

CREATE TABLE quizzes (
	id SERIAL PRIMARY KEY,
	course_page_id INTEGER REFERENCES course_pages,
	question TEXT
);

CREATE TABLE choices (
	id SERIAL PRIMARY KEY,
	quiz_id INTEGER REFERENCES quizzes,
	content TEXT,
	is_correct BOOLEAN
);

CREATE TABLE results (
	id SERIAL PRIMARY KEY,
	user_id INTEGER REFERENCES users,
	quiz_id INTEGER REFERENCES quizzes,
	is_correct BOOLEAN
);

CREATE TABLE participants (
	id SERIAL PRIMARY KEY,
	user_id INTEGER REFERENCES users,
	course_id INTEGER REFERENCES courses
);
