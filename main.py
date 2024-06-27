import flask

from flask import Flask
from flask_mysqldb import MySQL

from flask_restful import Api

from resources.student import Student
#from resources.instructor import Instructor
#from resources.course import Course 

from config import connection_string


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'koolele'
app.config['MYSQL_DB'] = 'database_name'
mysql = MySQL(app)

api = Api(app)


api.add_resource(Student, "/student/<int:student_id>")
#api.add_resource(Instructor, "/instructor/<int:id>")
#api.add_resource(Course, "/course/<int:id>")



if __name__ == '__main__':
    
    print(connection_string)
    app.run(debug=True)



@app.route('/')
def hello_world():
    return 'Hello, World!'
