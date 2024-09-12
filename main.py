import flask

from flask import Flask, request, jsonify, make_response

# the below are for configuring the token
import jwt
from functools import wraps
from datetime import datetime, timedelta

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

from setup import APP


APP.config['SECRET KEY'] = 'SECRET'

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



@APP.route('/')
def hello_world():
    return 'Hello, World!'


# used for logging into the API
@APP.route('/login', methods=['POST'])
def login():

    auth = request.authorization

    if auth and auth.password == '1':
        

        token = jwt.encode({
            'user':auth.username,
            'expiration': str(datetime.now() + timedelta(seconds=60))
        },
        
            APP.config['SECRET KEY']
        )

        return jsonify({'token': token})
    
    else:
        return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic Realm Authentication Failed'})


# used for decorating functions, demanding they nhave a valid token
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        
        if 'x-access-token' in request.headers:

            token = request.headers['x-access-token']

        if not token: return jsonify({"messsage": "token is missing"}, 401)

        try:
            data = jwt.decode(token, APP.config['SECRET KEY'])

        except:
            return jsonify({"Alert!": 'Invalid token'})

    
        return func(*args, **kwargs)
    
    return decorated

if __name__ == '__main__':
    
    APP.run(debug=True, host='0.0.0.0')

