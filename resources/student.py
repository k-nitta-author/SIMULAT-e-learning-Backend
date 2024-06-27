from datetime import datetime

from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from config import connection_string

from marshmallow import Schema, fields

engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
session = Session()


metadata = MetaData()
students_table = Table('student', metadata, autoload_with=engine)





class StudentSchema(Schema):
        given_name= fields.Str()
        middle_name= fields.Str()
        surname= fields.Str()
        date_of_birth= fields.Date()
        gender=fields.Str()
        enrollment_date=fields.Date()
        student_id=fields.Int()
        token_id=fields.Int()





class StudentModel:
    def __init__(self, dob=None, gender=None, enrollment_date=None, student_id=None, name=None, token_id=None):
        self.dob = dob
        self.gender = gender
        self.enrollment_date = enrollment_date
        self.id = student_id
        self.name = name
        self.token_id = token_id

# Resource class
class Student(Resource):
    def __init__(self):
        super().__init__()

        self.parser = reqparse.RequestParser()
        self.parser.add_argument("given_name", type=str, help="Given Name of Student")
        self.parser.add_argument("middle_name", type=str, help="Middle Name of Student")
        self.parser.add_argument("surname", type=str, help="Surname of Student")
        self.parser.add_argument("date_of_birth", type=str, help="DOB of Student")
        self.parser.add_argument("gender", type=str, help="Gender of Student")
        self.parser.add_argument("enrollment_date", type=str, help="Enrollment date of Student")
        self.parser.add_argument("token_id", type=str, help="Enrollment date of Student")


    def get(self, student_id):
        stmt = select(students_table).where(students_table.c.student_id == student_id)
        result = session.execute(stmt).fetchone()

        schema =StudentSchema()

        dump = schema.dump(result._mapping)

        if result:
            return dump, 200
        else:
            abort(404, message="Student not found")

    def put(self, student_id):
        args = self.parser.parse_args()

        # Check if the student already exists
        stmt = select(students_table).where(students_table.c.student_id == student_id)

        

        result = session.execute(stmt).fetchone()

        if result:
            # Update the existing student
            stmt = students_table.update().where(students_table.c.student_id == student_id).values(
            given_name=args['given_name'],
            middle_name=args['middle_name'],
            surname=args['surname'],
            gender=args['gender'],
            date_of_birth=parse_date(args['date_of_birth'], '%d-%m-%Y').date(),
            enrollment_date=parse_date(args['enrollment_date'], '%d-%m-%Y').date(),
            token_id=args['token_id']
            )
            session.execute(stmt)
            session.commit()
            return {student_id: args}, 200
        else:

            parse_date = datetime.strptime
        

            # Insert a new student
            stmt = students_table.insert().values(
            student_id=student_id,
            given_name=args['given_name'],
            middle_name=args['middle_name'],
            surname=args['surname'],
            gender=args['gender'],
            token_id=args['token_id'],

            

            date_of_birth=parse_date(args['date_of_birth'], '%d-%m-%Y').date(),
            enrollment_date=parse_date(args['enrollment_date'], '%d-%m-%Y').date()
            )
            session.execute(stmt)
            session.commit()
            return {student_id: args}, 201


    def delete(self, student_id):
        stmt = students_table.delete().where(students_table.c.student_id == student_id)
        session.execute(stmt)
        session.commit()
        return '', 204
