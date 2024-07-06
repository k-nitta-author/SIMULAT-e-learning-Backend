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
table = Table('content', metadata, autoload_with=engine)

# used to serialize data into non-python form for reading in JSON form
# see student.py for an example of proper class design. 
class ContentSchema(Schema):
        course_id= fields.Int()
        content_type= fields.Str()
        content_title= fields.Str()
        content_description= fields.Str()
        content_url=fields.Str()
        created_at=fields.Str()

# resource class
class Content(Resource):

    def __init__(self) -> None:
        super().__init__()

        self.parser = reqparse.RequestParser()

        # NECESSARY TO PARSE ALL JSON REQUEST ARGUMENTS.
        # SIMPLY ADD ALL DB PARAMETERS
        self.parser.add_argument('content_id', type=int, help="Given Name of course")
        self.parser.add_argument('course_id', type=int, help="Given Name of course")
        self.parser.add_argument('content_type', type=str, help="Given Name of course")
        self.parser.add_argument("content_title", type=str, help="desc of course")
        self.parser.add_argument("content_description", type=str, help="starting date of course")
        self.parser.add_argument("content_url", type=str, help="Surname of Student")
        self.parser.add_argument("created_at", type=str, help="")

    # basic GET request 
    def get(self, content_id):

        # select row from a table with a matching course id
        # present a result by executing the sql statement 
        stmt = select(table).where(table.c.content_id == content_id)
        result = session.execute(stmt).fetchone()

        print(result._mapping)

        # instantiate schema and serialize the data
        schema =ContentSchema()

        # if row is not empty, return accessed data
        # abort and return a 404 if there is no student
        if result:
            return schema.dump(result._mapping), 200
        else:
            abort(404, message="Course not found")

    def put(self, content_id):
        args = self.parser.parse_args()

        # Check if the instructor already exists
        stmt = select(table).where(table.c.content_id == content_id)

        

        result = session.execute(stmt).fetchone()

        if result:
            # Update the existing student      
            # 
            stmt = table.update().where(table.c.content_id == content_id).values(
            course_id=args['course_id'],
            content_type=args['content_type'],
            content_title=args['content_title'],
            content_description=args['content_description'],
            content_url=args['content_url'],
            created_at=args['created_at']
            )
            session.execute(stmt)
            session.commit()
            return {content_id: args}, 200
        else:
        

            # Insert a new instructor
            stmt = table.insert().values(
            course_id=args['course_id'],
            content_type=args['content_type'],
            content_title=args['content_title'],
            content_description=args['content_description'],
            content_url=args['content_url'],
            created_at=args['created_at']

            )
            session.execute(stmt)
            session.commit()
            return {content_id: args}, 201

    def delete(self, content_id):

        stmt = table.delete().where(table.c.content_id == content_id)
        session.execute(stmt)
        session.commit()
        return '', 204
