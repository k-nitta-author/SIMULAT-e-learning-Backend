from datetime import datetime

from flask import Flask
from flask_restful import Resource, reqparse, abort
from sqlalchemy import create_engine, Table, MetaData, select
from sqlalchemy.orm import sessionmaker
from config import connection_string

from marshmallow import Schema, fields

engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
session = Session()


metadata = MetaData()
table = Table('quiz', metadata, autoload_with=engine)


# used to serialize data into non-python form for reading in JSON form
# see student.py for an example of proper class design. 
class QuizSchema(Schema):
        content_id= fields.Int()
        quiz_title=fields.Str()
        description=fields.Str()
        time_limit=fields.Int()
        is_published=fields.Int()
        created_at=fields.Str()
        updated_at=fields.Str()

# resource class
class Quiz(Resource):

    def __init__(self) -> None:
        super().__init__()

        self.parser = reqparse.RequestParser()

        # NECESSARY TO PARSE ALL JSON REQUEST ARGUMENTS.
        # SIMPLY ADD ALL DB PARAMETERS

        self.parser = reqparse.RequestParser()
        self.parser.add_argument("content_id", type=int, help="Given Name of Student")
        self.parser.add_argument("quiz_title", type=str, help="Given Name of Student")
        self.parser.add_argument("description", type=str, help="Middle Name of Student")
        self.parser.add_argument("time_limit", type=int, help="Surname of Student")
        self.parser.add_argument("is_published", type=int, help="DOB of Student")
        self.parser.add_argument("created_at", type=str, help="Gender of Student")
        self.parser.add_argument("updated_at", type=str, help="Gender of Student")

    # basic GET request 
    def get(self, quiz_id):

        # select row from a table with a matching instructor id
        # present a result by executing the sql statement 
        stmt = select(table).where(table.c.quiz_id == quiz_id)
        result = session.execute(stmt).fetchone()

        # instantiate schema and serialize the data
        schema =QuizSchema()
        dump = schema.dump(result._mapping)


        # if row is not empty, return accessed data
        # abort and return a 404 if there is no student
        if result:
            return dump, 200
        else:
            abort(404, message="Student not found")

    def put(self, quiz_id):
        args = self.parser.parse_args()

        # Check if the instructor already exists
        stmt = select(table).where(table.c.quiz_id == quiz_id)

        

        result = session.execute(stmt).fetchone()

        if result:
            # Update the existing student
            stmt = table.update().where(table.c.quiz_id == quiz_id).values(
            content_id=args['content_id'],
            quiz_title=args['quiz_title'],
            description=args['description'],
            time_limit=args['time_limit'],
            is_published=args['is_published'],
            created_at=args['created_at'],
            updated_at=args['updated_at']

            )
            session.execute(stmt)
            session.commit()
            return {quiz_id: args}, 200
        else:

            parse_date = datetime.strptime
        

            # Insert a new instructor
            stmt = table.insert().values(
            content_id=args['content_id'],
            quiz_title=args['quiz_title'],
            description=args['description'],
            time_limit=args['time_limit'],
            is_published=args['is_published'],
            created_at=args['created_at'],
            updated_at=args['updated_at']
            )
            session.execute(stmt)
            session.commit()
            return {quiz_id: args}, 201

    def delete(self, quiz_id):

        stmt = table.delete().where(table.c.quiz_id == quiz_id)
        session.execute(stmt)
        session.commit()
        return '', 204