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
table = Table('dailychallengescore', metadata, autoload_with=engine)


# used to serialize data into non-python form for reading in JSON form
# see student.py for an example of proper class design. 
class DailyChallengeScoreSchema(Schema):
        score= fields.Int()
        submission_date=fields.Str()
        challenge_id=fields.Int()
        student_id=fields.Str()

# resource class
class DailyChallenge(Resource):

    def __init__(self) -> None:
        super().__init__()

        self.parser = reqparse.RequestParser()

        # NECESSARY TO PARSE ALL JSON REQUEST ARGUMENTS.
        # SIMPLY ADD ALL DB PARAMETERS

        self.parser = reqparse.RequestParser()
        self.parser.add_argument("score", type=int, help="Given Name of Student")
        self.parser.add_argument("submission_date", type=int, help="Given Name of Student")
        self.parser.add_argument("challenge_id", type=int, help="DOB of Student")
        self.parser.add_argument("student_id", type=int, help="Gender of Student")

    # basic GET request 
    def get(self, challenge_score_id):

        # select row from a table with a matching instructor id
        # present a result by executing the sql statement 
        stmt = select(table).where(table.c.challenge_score_id == challenge_score_id)
        result = session.execute(stmt).fetchone()

        # instantiate schema and serialize the data
        schema =DailyChallengeScoreSchema()
        dump = schema.dump(result._mapping)


        # if row is not empty, return accessed data
        # abort and return a 404 if there is no student
        if result:
            return dump, 200
        else:
            abort(404, message="Student not found")

    def put(self, challenge_score_id):
        args = self.parser.parse_args()

        # Check if the instructor already exists
        stmt = select(table).where(table.c.challenge_score_id == challenge_score_id)

        

        result = session.execute(stmt).fetchone()

        if result:
            # Update the existing student
            stmt = table.update().where(table.c.challenge_id == challenge_score_id).values(
            score=args['score'],
            submission_date=args['submission_date'],
            challenge_id=args['challenge_id'],
            student_id=args['student_id'],

            )
            session.execute(stmt)
            session.commit()
            return {challenge_score_id: args}, 200
        else:
        

            # Insert a new instructor
            stmt = table.insert().values(
            score=args['score'],
            submission_date=args['submission_date'],
            challenge_id=args['challenge_id'],
            student_id=args['student_id'],

        
            )
            session.execute(stmt)
            session.commit()
            return {challenge_score_id: args}, 201

    def delete(self, challenge_score_id):

        stmt = table.delete().where(table.c.challenge_score_id == challenge_score_id)
        session.execute(stmt)
        session.commit()
        return '', 204