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
table = Table('quizscore', metadata, autoload_with=engine)


# used to serialize data into non-python form for reading in JSON form
# see student.py for an example of proper class design. 
class QuizScoreSchema(Schema):
        quiz_score_id= fields.Int()
        score=fields.Int()
        submission_date=fields.Str()
        quiz_id=fields.Int()
        student_id=fields.Int()

# resource class
class QuizScore(Resource):

    def __init__(self) -> None:
        super().__init__()

        self.parser = reqparse.RequestParser()

        # NECESSARY TO PARSE ALL JSON REQUEST ARGUMENTS.
        # SIMPLY ADD ALL DB PARAMETERS

        self.parser = reqparse.RequestParser()
        self.parser.add_argument("quiz_score_id", type=int, help="Given Name of Student")
        self.parser.add_argument("score", type=int, help="Given Name of Student")
        self.parser.add_argument("submission_date", type=str, help="Middle Name of Student")
        self.parser.add_argument("quiz_id", type=int, help="Surname of Student")
        self.parser.add_argument("student_id", type=int, help="DOB of Student")

    # basic GET request 
    def get(self, quiz_score_id):

        # select row from a table with a matching instructor id
        # present a result by executing the sql statement 
        stmt = select(table).where(table.c.quiz_score_id == quiz_score_id)
        result = session.execute(stmt).fetchone()

        # instantiate schema and serialize the data
        schema =QuizScoreSchema()
        dump = schema.dump(result._mapping)


        # if row is not empty, return accessed data
        # abort and return a 404 if there is no student
        if result:
            return dump, 200
        else:
            abort(404, message="Student not found")

    def put(self, quiz_score_id):
        args = self.parser.parse_args()

        # Check if the instructor already exists
        stmt = select(table).where(table.c.quiz_score_id == quiz_score_id)

        

        result = session.execute(stmt).fetchone()

        if result:
            # Update the existing student
            stmt = table.update().where(table.c.quiz_score_id == quiz_score_id).values(
            quiz_score_id=args['quiz_score_id'],
            score=args['score'],
            submission_date=args['submission_date'],
            quiz_id=args['quiz_id'],
            student_id=args['student_id']



            # Careful around dates; they need to be formatted dd-mm-YYYY according to db

            )
            session.execute(stmt)
            session.commit()
            return {quiz_score_id: args}, 200
        else:        

            # Insert a new instructor
            stmt = table.insert().values(
            quiz_score_id=args['quiz_score_id'],
            score=args['score'],
            submission_date=args['submission_date'],
            quiz_id=args['quiz_id'],
            student_id=args['student_id']
            

            )
            session.execute(stmt)
            session.commit()
            return {quiz_score_id: args}, 201

    def delete(self, quiz_score_id):

        stmt = table.delete().where(table.c.quiz_score_id == quiz_score_id)
        session.execute(stmt)
        session.commit()
        return '', 204