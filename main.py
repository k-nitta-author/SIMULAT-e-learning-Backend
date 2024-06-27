import flask

from flask import Flask
from flask_restful import Api

from resources.student import Student
from resources.instructor import Instructor
#from resources.course import Course 

from config import connection_string


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)

api = Api(app)


api.add_resource(Student, "/student/<int:student_id>")
api.add_resource(Instructor, "/instructor/<int:instructor_id>")
#api.add_resource(Course, "/course/<int:id>")



if __name__ == '__main__':
    
    app.run(debug=True)



@app.route('/')
def hello_world():
    return 'Hello, World!'
