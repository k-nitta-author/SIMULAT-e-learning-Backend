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
table = Table('assignmentscore', metadata, autoload_with=engine)

# used to serialize data into non-python form for reading in JSON form
# see student.py for an example of proper class design. 
class AssignmentScoreSchema(Schema):
        score= fields.Int()
        submission_date= fields.Int()
        assignment_id= fields.Int()
        student_id= fields.Int()

# resource class
class AssignmentScore(Resource):

    def __init__(self) -> None:
        super().__init__()

        self.parser = reqparse.RequestParser()

        # NECESSARY TO PARSE ALL JSON REQUEST ARGUMENTS.
        # SIMPLY ADD ALL DB PARAMETERS
        self.parser.add_argument('score', type=int, help="Given Name of course")
        self.parser.add_argument('submission_date', type=str, help="Given Name of course")
        self.parser.add_argument('assignment_id', type=str, help="Given Name of course")
        self.parser.add_argument("student_id", type=str, help="desc of course")


    # basic GET request 
    def get(self, assignment_score_id):

        # select row from a table with a matching course id
        # present a result by executing the sql statement 
        stmt = select(table).where(table.c.assignment_score_id == assignment_score_id)
        result = session.execute(stmt).fetchone()

        print(result._mapping)

        # instantiate schema and serialize the data
        schema =AssignmentScoreSchema()

        # if row is not empty, return accessed data
        # abort and return a 404 if there is no student
        if result:
            return schema.dump(result._mapping), 200
        else:
            abort(404, message="Course not found")

    def put(self, assignment_score_id):
        args = self.parser.parse_args()

        # Check if the instructor already exists
        stmt = select(table).where(table.c.assignment_score_id == assignment_score_id)

        

        result = session.execute(stmt).fetchone()

        if result:
            # Update the existing student      
            # 
            stmt = table.update().where(table.c.assignment_score_id == assignment_score_id).values(
            score=args['score'],
            submission_date=args['submission_date'],
            assignment_id=args['assignment_id'],
            student_id=args['student_id']
            )

            session.execute(stmt)
            session.commit()
            return {assignment_score_id: args}, 200
        else:
        

            # Insert a new instructor
            stmt = table.insert().values(

            score=args['score'],
            submission_date=args['submission_date'],
            assignment_id=args['assignment_id'],
            student_id=args['student_id']

            )
            session.execute(stmt)
            session.commit()
            return {assignment_score_id: args}, 201

    def delete(self, assignment_score_id):

        stmt = table.delete().where(table.c.assignment_score_id == assignment_score_id)
        session.execute(stmt)
        session.commit()
        return '', 204
