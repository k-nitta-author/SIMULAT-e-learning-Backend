from datetime import datetime

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

from config import connection_string

from tables import User
from tables import Course
from tables import CourseEnrollment
from tables import Assignment
from tables import AssignmentScore
from tables import Quiz
from tables import QuizScore
from tables import LessonMaterial
from tables import Content
from tables import DailyChallenge
from tables import DailyChallengeScore
from tables import Term
from tables import Badge

from tables import Gender

from datetime import datetime

from flask import Flask
from werkzeug.security import generate_password_hash


ENGINE = create_engine(connection_string)
session = sessionmaker(bind=ENGINE)

SESSION = session()

APP = Flask(__name__)
APP.secret_key = "secret_key"

def add_to_session(func):
    

    def wrap(*args, **kwargs):
        obj = func()


        session.add(obj)
        session.commit()


    return wrap

@add_to_session
def create_default_admin() -> User:
    ad_user = User()
    
    ad_user.email = "k.nitta.it@gmail.com"
    ad_user.name_given = "kennichi"
    ad_user.name_last = "nitta"

    ad_user.is_student = False
    ad_user.is_instructor= False
    ad_user.is_admin= True

    ad_user.gender = Gender.male

    ad_user.progress_score = 0

    ad_user.username = "k.nitta.it"

    ad_user.password = generate_password_hash("password", method='pbkdf2:sha256')

    ad_user.is_super_admin = False

    return ad_user

@add_to_session
def create_default_badge() -> User:
    badge = Badge()
    
    badge.description = "asddaskjhdkahsdkahdk"
    badge.name = "Studious Student"
    badge.pts_required = 100
    
    return badge

@add_to_session
def create_course() -> Course:

    c = Course()

    c.course_code = "AAA"
    c.course_name = "EWQ WRE"
    
    c.description = "sadasd skajhd kajshdkj asdh"
    
    c.created_at = datetime.now()
    
    c.instructor_id = 2
    c.term_id = 1

    c.is_published = False
    c.updated_at = datetime.now()


    return c

@add_to_session
def create_course_enrollment() -> CourseEnrollment:
    
    e = CourseEnrollment()

    e.enroll_date = datetime.now()

    e.course_id = 1
    e.user_id = 3

    return e

@add_to_session
def create_default_student() -> User:
    default_student = User()
    
    default_student.email = "j.fakename.us@gmail.com"
    default_student.name_given = "John"
    default_student.name_last = "Fakename"

    default_student.gender = Gender.male

    default_student.is_student = True
    default_student.is_instructor= False
    default_student.is_admin= False

    default_student.progress_score = 0

    default_student.username = "j_fakename"
    default_student.password = generate_password_hash("password", method='pbkdf2:sha256')

    default_student.is_super_admin = False

    return default_student

@add_to_session
def create_default_instructor() -> User:
    default_instructor = User()
    
    default_instructor.email = "j.teacherman.us@gmail.com"
    default_instructor.name_given = "John"
    default_instructor.name_last = "teacherman"

    default_instructor.gender = Gender.male


    default_instructor.is_student = False
    default_instructor.is_instructor= True
    default_instructor.is_admin= False

    default_instructor.progress_score = 0


    default_instructor.username = "j_teacherman"
    default_instructor.password = generate_password_hash("password", method='pbkdf2:sha256')

    default_instructor.is_super_admin = False

    return default_instructor

@add_to_session
def create_default_super_admin() -> User:
    super_admin = User()
    
    super_admin.email = "a.simpson.@omail.com"
    super_admin.name_given = "Sanson"
    super_admin.name_last = "Alba"

    super_admin.gender = Gender.female


    super_admin.is_student = False
    super_admin.is_instructor= False
    super_admin.is_admin= False

    super_admin.progress_score = 0

    super_admin.username = "root_admin"
    super_admin.password = generate_password_hash("password", method='pbkdf2:sha256')

    super_admin.is_super_admin = True

    return super_admin

@add_to_session
def create_default_challenge() -> DailyChallenge:
    
    c = DailyChallenge()

    c.content_id = 1
    c.is_published = False
    c.publication_date = None
    c.updated_at = datetime.now()
    c.created_at = datetime.now()

    return c

@add_to_session
def create_daily_challenge_score() ->  DailyChallengeScore:

    s = DailyChallengeScore()

    s.score = 30
    s.submission_date = "2001-1-1"
    s.user_id = 1
    s.challenge_id = 1 

    return s

@add_to_session
def create_default_lesson() -> LessonMaterial:
    
    l = LessonMaterial()

    l.content_id = 1
    l.description = "asdjaksdhjakshd"
    l.material_title = "sadasdasd"
    l.material_url = "asdasdjaksdj"
    l.created_at = datetime.now()

    return l

@add_to_session
def create_default_content() -> Content:
    
    c = Content()

    c.course_id = 1
    c.title = "asd aksdj sadh"    
    c.created_at = datetime.now()
    c.description = "asd asdhhasdkj ashdkh"
    c.url = "asdkasjd kajsd"
    c.type = "asdasd"
    c.term_id = 1
    
    return c

@add_to_session
def create_default_assignment() -> Assignment:
    
    a = Assignment()

    a.assignment_title = "asd asdii jkad"
    a.instructions = "asdkj lkjasldj lkasdj"
    a.description = "ashdkjhasd kash ashdkahsdk"
    a.grading_criteria = "asdjha sdgh jagshd"
    a.max_score = 30
    a.submission_format = "docx"
    a.updated_at = datetime.now()
    a.created_at = datetime.now()
    a.deadline = "2023-8-2"
    a.content_id = 1
    a.term_id = 1

    return a

@add_to_session
def create_assignment_score() -> AssignmentScore:

    s = AssignmentScore()

    s.assignment_id = 1
    s.score = 30
    s.submission_date = "2001-12-12"
    s.student_id = 1

    return s

@add_to_session
def create_quiz() -> Quiz:
    q = Quiz()

    q.content_id = 1
    
    q.quiz_title = "Quiz 1"
    q.description = "asdasd"
    q.is_published = False
    q.time_limit = 30
    q.term_id = 1
    
    return q

@add_to_session
def create_quiz_score() -> QuizScore:
    
    qs = QuizScore()

    qs.quiz_id = 1
    qs.score = 30
    qs.student_id = 1
    qs.submission_date = "2024-6-4"

    return qs

@add_to_session
def create_term() -> Term:

    t = Term()

    t.school_year_end = datetime(2024, 2, 1)
    t.school_year_start = datetime(2024, 5, 11)

    return t

if __name__ == "__main__":
    

    engine = create_engine(connection_string)
    with Session(engine) as session:

        admin = create_default_admin()
        instructor = create_default_instructor()
        student = create_default_student()
        root_admin = create_default_super_admin()

        term = create_term()
        
        course = create_course()
        enrollment = create_course_enrollment()

        content = create_default_content()

        assignment = create_default_assignment()
        assignment_score = create_assignment_score()

        quiz = create_quiz()
        quiz_score = create_quiz_score()

        challenge = create_default_challenge()
        challenge_score = create_daily_challenge_score()
        
        lesson_material = create_default_lesson()

        badge = create_default_badge()

        session.commit()