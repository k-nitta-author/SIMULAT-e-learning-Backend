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


from config import connection_string


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)

api = Api(app)


api.add_resource(Student, "/student/<int:student_id>")
api.add_resource(Instructor, "/instructor/<int:instructor_id>")

api.add_resource(Course, "/course/<int:course_id>")
api.add_resource(CourseEnrollment, "/enrollment/<int:enrollment_id>")

api.add_resource(Quiz, "/quiz/<int:quiz_id>")
api.add_resource(QuizScore, "/quiz_score/<int:quiz_score_id>")

api.add_resource(Content, "/content/<int:content_id>")
api.add_resource(LessonMaterial, "/lesson_material/<int:material_id>")





if __name__ == '__main__':
    
    app.run(debug=True)



@app.route('/')
def hello_world():
    return 'Hello, World!'
