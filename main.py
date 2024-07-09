import flask

from flask import Flask
from flask_restful import Api

from resources.student import Student
from resources.instructor import Instructor
from resources.course import Course 
from resources.quiz import Quiz
from resources.quiz_score import QuizScore
from resources.content import Content
from resources.lesson_material import LessonMaterial
from resources.course_enrollment import CourseEnrollment
from resources.assignment import Assignment
from resources.assignment_score import AssignmentScore
from resources.daily_challenge import DailyChallenge
from resources.daily_challenge_score import DailyChallengeScore

app = Flask(__name__)

api = Api(app)

# Add each resource class to the api through dependency injection
# each call of add_resource injects the class which the api instantiates
# the second parameter is the URL and URI specified

api.add_resource(Student, "/student/<int:student_id>")
api.add_resource(Instructor, "/instructor/<int:instructor_id>")

api.add_resource(Course, "/course/<int:course_id>")
api.add_resource(CourseEnrollment, "/enrollment/<int:enrollment_id>")

api.add_resource(Quiz, "/quiz/<int:quiz_id>")
api.add_resource(QuizScore, "/quiz_score/<int:quiz_score_id>")

api.add_resource(Content, "/content/<int:content_id>")
api.add_resource(LessonMaterial, "/lesson_material/<int:material_id>")

api.add_resource(DailyChallenge, "/challenge/<int:challenge_id>")
api.add_resource(DailyChallengeScore, "/challenge_score/<int:challenge_score_id>")

api.add_resource(Assignment, "/assignment/<int:assignment_id>")
api.add_resource(AssignmentScore, "/assignment_score/<int:assignment_score_id>")

@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    
    app.run(debug=True, host='0.0.0.0')

