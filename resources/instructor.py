from datetime import datetime

from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
from sqlalchemy import create_engine, Table, MetaData, select
from sqlalchemy.orm import sessionmaker
from config import connection_string

from marshmallow import Schema, fields

engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
session = Session()


metadata = MetaData()
table = Table('instructor', metadata, autoload_with=engine)


# used to serialize data into non-python form for reading in JSON form
# see student.py for an example of proper class design. 
class InstructorSchema(Schema):
        given_name= fields.Str()
        middle_name= fields.Str()
        surname= fields.Str()
        date_of_birth= fields.Date()
        gender=fields.Str()
        instructor_id=fields.Int()

# resource class
class Instructor(Resource):

    def __init__(self) -> None:
        super().__init__()

        self.parser = reqparse.RequestParser()

        # NECESSARY TO PARSE ALL JSON REQUEST ARGUMENTS.
        # SIMPLY ADD ALL DB PARAMETERS

        self.parser = reqparse.RequestParser()
        self.parser.add_argument("given_name", type=str, help="Given Name of Student")
        self.parser.add_argument("middle_name", type=str, help="Middle Name of Student")
        self.parser.add_argument("surname", type=str, help="Surname of Student")
        self.parser.add_argument("date_of_birth", type=str, help="DOB of Student")
        self.parser.add_argument("gender", type=str, help="Gender of Student")

    # basic GET request 
    def get(self, instructor_id):

        # select row from a table with a matching instructor id
        # present a result by executing the sql statement 
        stmt = select(table).where(table.c.instructor_id == instructor_id)
        result = session.execute(stmt).fetchone()

        # instantiate schema and serialize the data
        schema =InstructorSchema()
        dump = schema.dump(result._mapping)


        # if row is not empty, return accessed data
        # abort and return a 404 if there is no student
        if result:
            return dump, 200
        else:
            abort(404, message="Student not found")

    def put(self, instructor_id):
        args = self.parser.parse_args()

        # Check if the instructor already exists
        stmt = select(table).where(table.c.instructor_id == instructor_id)

        

        result = session.execute(stmt).fetchone()

        if result:
            # Update the existing student
            stmt = table.update().where(table.c.instructor_id == instructor_id).values(
            given_name=args['given_name'],
            middle_name=args['middle_name'],
            surname=args['surname'],
            gender=args['gender'],

            
            # Careful around dates; they need to be formatted dd-mm-YYYY according to db

            date_of_birth=parse_date(args['date_of_birth'], '%d-%m-%Y').date(),
            )
            session.execute(stmt)
            session.commit()
            return {instructor_id: args}, 200
        else:

            parse_date = datetime.strptime
        

            # Insert a new instructor
            stmt = table.insert().values(
            instructor_id=instructor_id,
            given_name=args['given_name'],
            middle_name=args['middle_name'],
            surname=args['surname'],
            gender=args['gender'],
            

            date_of_birth=parse_date(args['date_of_birth'], '%d-%m-%Y').date(),
            )
            session.execute(stmt)
            session.commit()
            return {instructor_id: args}, 201

    def delete(self, instructor_id):

        stmt = table.delete().where(table.c.instructor_id == instructor_id)
        session.execute(stmt)
        session.commit()
        return '', 204

