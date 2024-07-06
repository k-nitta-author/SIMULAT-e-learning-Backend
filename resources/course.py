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
table = Table('course', metadata, autoload_with=engine)



# used to serialize data into non-python form for reading in JSON form
# see student.py for an example of proper class design. 
class CourseSchema(Schema):
        course_code= fields.Int()
        course_name= fields.Str()
        description= fields.Str()
        start_date= fields.Str()
        instructor_id=fields.Str()
        is_published=fields.Int()
        end_date=fields.Str()
        created_at=fields.Str()
        updated_at=fields.Str()

# resource class
class Course(Resource):

    def __init__(self) -> None:
        super().__init__()

        self.parser = reqparse.RequestParser()

        # NECESSARY TO PARSE ALL JSON REQUEST ARGUMENTS.
        # SIMPLY ADD ALL DB PARAMETERS
        self.parser.add_argument('course_name', type=str, help="Given Name of course")
        self.parser.add_argument('course_code', type=int, help="Given Name of course")
        self.parser.add_argument("description", type=str, help="desc of course")
        self.parser.add_argument("start_date", type=str, help="starting date of course")
        self.parser.add_argument("instructor_id", type=int, help="Surname of Student")
        self.parser.add_argument("is_published", type=int, help="")
        self.parser.add_argument("end_date", type=str, help="")
        self.parser.add_argument("created_at", type=str, help="Enrollment date of Student")
        self.parser.add_argument("updated_at", type=str, help="Enrollment date of Student")



    # basic GET request 
    def get(self, course_id):

        # select row from a table with a matching course id
        # present a result by executing the sql statement 
        stmt = select(table).where(table.c.course_id == course_id)
        result = session.execute(stmt).fetchone()

        print(result._mapping)

        # instantiate schema and serialize the data
        schema =CourseSchema()
        dump = schema.dump(result._mapping)


        # if row is not empty, return accessed data
        # abort and return a 404 if there is no student
        if result:
            return dump, 200
        else:
            abort(404, message="Course not found")

    def put(self, course_id):
        args = self.parser.parse_args()

        # Check if the instructor already exists
        stmt = select(table).where(table.c.course_id == course_id)

        

        result = session.execute(stmt).fetchone()

        if result:
            # Update the existing student            
            
            stmt = table.update().where(table.c.course_id == course_id).values(
            course_name=args['course_name'],
            course_code=args['course_code'],
            start_date=args['start_date'],
            instructor_id=args['instructor_id'],
            is_published=args['is_published'],
            end_date=args['end_date'],
            created_at=args['created_at'],
            description=args['description'],
            updated_at=args['updated_at'],
            )
            session.execute(stmt)
            session.commit()
            return {course_id: args}, 200
        else:
        

            # Insert a new instructor
            stmt = table.insert().values(
            course_id=course_id,
            course_name=args['course_name'],
            course_code=args['course_code'],
            description=args['description'],
            start_date=args['start_date'],
            instructor_id=args['instructor_id'],
            is_published=args['is_published'],
            end_date=args['end_date'],
            created_at=args['created_at'],
            updated_at=args['updated_at'],

            )
            session.execute(stmt)
            session.commit()
            return {course_id: args}, 201

    def delete(self, course_id):

        stmt = table.delete().where(table.c.course_id == course_id)
        session.execute(stmt)
        session.commit()
        return '', 204
