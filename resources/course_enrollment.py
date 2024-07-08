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
table = Table('courseenrollment', metadata, autoload_with=engine)

# used to serialize data into non-python form for reading in JSON form
# see student.py for an example of proper class design. 
class CourseEnrollmentSchema(Schema):
        enrollment_date= fields.Int()
        course_id= fields.Str()
        student_id= fields.Str()

# resource class
class CourseEnrollment(Resource):

    def __init__(self) -> None:
        super().__init__()

        self.parser = reqparse.RequestParser()

        # NECESSARY TO PARSE ALL JSON REQUEST ARGUMENTS.
        # SIMPLY ADD ALL DB PARAMETERS
        self.parser.add_argument('enrollment_date', type=str, help="Given Name of course")
        self.parser.add_argument('course_id', type=int, help="Given Name of course")
        self.parser.add_argument("student_id", type=str, help="desc of course")

    # basic GET request 
    def get(self, enrollment_id):

        # select row from a table with a matching course id
        # present a result by executing the sql statement 
        stmt = select(table).where(table.c.enrollment_id == enrollment_id)
        result = session.execute(stmt).fetchone()

        print(result._mapping)

        # instantiate schema and serialize the data
        schema =CourseEnrollmentSchema()
        dump = schema.dump(result._mapping)


        # if row is not empty, return accessed data
        # abort and return a 404 if there is no student
        if result:
            return dump, 200
        else:
            abort(404, message="Course not found")

    def put(self, enrollment_id):
        args = self.parser.parse_args()

        # Check if the instructor already exists
        stmt = select(table).where(table.c.enrollment_id == enrollment_id)

        

        result = session.execute(stmt).fetchone()

        if result:
            # Update the existing student            
            
            stmt = table.update().where(table.c.enrollment_id == enrollment_id).values(
            enrollment_date=args['enrollment_date'],
            course_id=args['course_id'],
            student_id=args['student_id']

            )
            session.execute(stmt)
            session.commit()
            return {enrollment_id: args}, 200
        else:
        

            # Insert a new instructor
            stmt = table.insert().values(
            enrollment_date=args['enrollment_date'],
            course_id=args['course_id'],
            student_id=args['student_id']


            )
            session.execute(stmt)
            session.commit()
            return {enrollment_id: args}, 201

    def delete(self, enrollment_id):

        stmt = table.delete().where(table.c.enrollment_id == enrollment_id)
        session.execute(stmt)
        session.commit()
        return '', 204
