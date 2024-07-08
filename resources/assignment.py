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
table = Table('assignment', metadata, autoload_with=engine)

# used to serialize data into non-python form for reading in JSON form
# see student.py for an example of proper class design. 
class AssignmentSchema(Schema):
        assignment_title= fields.Str()
        content_id= fields.Int()
        description= fields.Str()
        deadline= fields.Str()
        max_score=fields.Int()
        file_url=fields.Str()
        grading_criteria= fields.Str()
        instructions=fields.Str()
        created_at=fields.Str()
        submission_format=fields.Str()
        updated_at=fields.Str()

# resource class
class Assignment(Resource):

    def __init__(self) -> None:
        super().__init__()

        self.parser = reqparse.RequestParser()

        # NECESSARY TO PARSE ALL JSON REQUEST ARGUMENTS.
        # SIMPLY ADD ALL DB PARAMETERS
        self.parser.add_argument('content_id', type=int, help="Given Name of course")
        self.parser.add_argument('assignment_title', type=str, help="Given Name of course")
        self.parser.add_argument('description', type=str, help="Given Name of course")
        self.parser.add_argument("deadline", type=str, help="desc of course")
        self.parser.add_argument("max_score", type=int, help="starting date of course")
        self.parser.add_argument("file_url", type=str, help="Surname of Student")
        self.parser.add_argument("grading_criteria", type=str, help="")
        self.parser.add_argument("instructions", type=str, help="")
        self.parser.add_argument("submission_format", type=str, help="")
        self.parser.add_argument("is_published", type=int, help="")
        self.parser.add_argument("created_at", type=str, help="")
        self.parser.add_argument("updated_at", type=str, help="")

    # basic GET request 
    def get(self, assignment_id):

        # select row from a table with a matching course id
        # present a result by executing the sql statement 
        stmt = select(table).where(table.c.assignment_id == assignment_id)
        result = session.execute(stmt).fetchone()

        print(result._mapping)

        # instantiate schema and serialize the data
        schema =AssignmentSchema()

        # if row is not empty, return accessed data
        # abort and return a 404 if there is no student
        if result:
            return schema.dump(result._mapping), 200
        else:
            abort(404, message="Course not found")

    def put(self, assignment_id):
        args = self.parser.parse_args()

        # Check if the instructor already exists
        stmt = select(table).where(table.c.assignment_id == assignment_id)

        

        result = session.execute(stmt).fetchone()

        if result:
            # Update the existing student      
            # 
            stmt = table.update().where(table.c.assignment_id == assignment_id).values(
            assignment_title=args['assignment_title'],
            content_id=args['content_id'],
            description=args['description'],
            deadline=args['deadline'],
            max_score=args['max_score'],
            file_url=args['file_url'],
            grading_criteria=args['grading_criteria'],
            instructions=args['instructions'],
            submission_format=args['submission_format'],
            created_at=args['created_at'],
            updated_at=args['updated_at']
            )

            session.execute(stmt)
            session.commit()
            return {assignment_id: args}, 200
        else:
        

            # Insert a new instructor
            stmt = table.insert().values(
            assignment_title=args['assignment_title'],
            content_id=args['content_id'],
            description=args['description'],
            deadline=args['deadline'],
            max_score=args['max_score'],
            file_url=args['file_url'],
            grading_criteria=args['grading_criteria'],
            instructions=args['instructions'],
            submission_format=args['submission_format'],
            created_at=args['created_at'],
            updated_at=args['updated_at']

            )
            session.execute(stmt)
            session.commit()
            return {assignment_id: args}, 201

    def delete(self, assignment_id):

        stmt = table.delete().where(table.c.assignment_id == assignment_id)
        session.execute(stmt)
        session.commit()
        return '', 204
