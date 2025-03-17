import flask

from flask import Flask, request, jsonify, make_response, session
from datetime import datetime, timedelta

# the below are for configuring the token
import jwt
from functools import wraps
from os import environ
from flask_cors import CORS
from setup import APP, SESSION

from resources.user import UserResource
from resources.course import CourseResource
from resources.course_enrollment import CourseEnrollmentResource
from resources.content import ContentResource
from resources.challenge import DailyChallengeResource
from resources.challenge_score import DailyChallengeScoreResource
from resources.quiz import QuizResource
from resources.quiz_score import QuizScoreResource
from resources.lesson_material import LessonMaterialResource
from resources.assignment import AssignmentResource
from resources.assignment_score import AssignmentScoreResource
from resources.badge import BadgeResource
from resources.term import TermResource
from resources.studygroup import StudyGroupResource
from resources.bulletin_post import BulletinResource

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker

from setup import APP

# enable cors
cors = CORS(APP, resources={r"/*": {"origins": "*"}})

APP.config['SECRET KEY'] = environ.get("SECRET_KEY")

# Set session timeout
APP.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Set up the database
database_url = environ.get("CONNECTION_STRING")
if not database_url:
    raise RuntimeError("CONNECTION_STRING environment variable not set")

APP.config['SQLALCHEMY_DATABASE_URI'] = database_url
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_timeout': 30,  # Set the pool timeout to 30 seconds
    'pool_recycle': 1800  # Recycle connections every 30 minutes
}

db = SQLAlchemy(APP)

with APP.app_context():
    engine = db.engine
    Session = sessionmaker(bind=engine)
    SESSION = scoped_session(Session)

@APP.teardown_request
def teardown_request(exception=None):
    # Remove the scoped session
    SESSION.remove()

user_resource = UserResource()
course_resource = CourseResource()
course_enrollment_resource = CourseEnrollmentResource()
content_resource = ContentResource()
challenege_resource = DailyChallengeResource()
challenege_score_resource = DailyChallengeScoreResource()

quiz_resource = QuizResource()
quiz_score_resource = QuizScoreResource()

material_resource = LessonMaterialResource()
assignemnt_res = AssignmentResource()
assignment_score_res = AssignmentScoreResource()

badge_res = BadgeResource()
term_res = TermResource()
study_group = StudyGroupResource()
bulletin_res = BulletinResource()


if __name__ == '__main__':
    APP.run(debug=True, host='0.0.0.0', port=10000)