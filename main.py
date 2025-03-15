import flask
from flask import Flask, request, jsonify, make_response, session
from datetime import datetime, timedelta
import jwt
from functools import wraps
from os import environ
from flask_cors import CORS
from setup import APP, SESSION, db

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

# enable cors
cors = CORS(APP, resources={r"/*": {"origins": "*"}})

# register all routes
user_resource = UserResource()
course_resource = CourseResource()
course_enrollment_resource = CourseEnrollmentResource()
content_resource = ContentResource()
daily_challenge_resource = DailyChallengeResource()
daily_challenge_score_resource = DailyChallengeScoreResource()

quiz_resource = QuizResource()
quiz_score_resource = QuizScoreResource()

lesson_material_resource = LessonMaterialResource()
assignment_resource = AssignmentResource()
assignment_score_resource = AssignmentScoreResource()

badge_resource = BadgeResource()
term_resource = TermResource()
study_group_resource = StudyGroupResource()

if __name__ == '__main__':
    APP.run(debug=True, host='0.0.0.0', port=10000)

