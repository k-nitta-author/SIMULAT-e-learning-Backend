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
table = Table('lessonmaterial', metadata, autoload_with=engine)

# used to serialize data into non-python form for reading in JSON form
# see student.py for an example of proper class design. 
class LessonMaterialSchema(Schema):
        content_id= fields.Int()
        material_title= fields.Str()
        description= fields.Str()
        material_url=fields.Str()
        created_at=fields.Str()

# resource class
class LessonMaterial(Resource):

    def __init__(self) -> None:
        super().__init__()

        self.parser = reqparse.RequestParser()

        # NECESSARY TO PARSE ALL JSON REQUEST ARGUMENTS.
        # SIMPLY ADD ALL DB PARAMETERS
        self.parser.add_argument('content_id', type=int, help="Given Name of course")
        self.parser.add_argument('material_title', type=str, help="Given Name of course")
        self.parser.add_argument('description', type=str, help="Given Name of course")
        self.parser.add_argument('material_url', type=str, help="Given Name of course")
        self.parser.add_argument('created_at', type=str, help="Given Name of course")

    # basic GET request 
    def get(self, material_id):

        # select row from a table with a matching course id
        # present a result by executing the sql statement 
        stmt = select(table).where(table.c.material_id == material_id)
        result = session.execute(stmt).fetchone()

        print(result._mapping)

        # instantiate schema and serialize the data
        schema =LessonMaterialSchema()
        dump = schema.dump(result._mapping)


        # if row is not empty, return accessed data
        # abort and return a 404 if there is no student
        if result:
            return dump, 200
        else:
            abort(404, message="Course not found")

    def put(self, material_id):
        args = self.parser.parse_args()

        # Check if the instructor already exists
        stmt = select(table).where(table.c.material_id == material_id)

        

        result = session.execute(stmt).fetchone()

        if result:
            # Update the existing student            
            
            stmt = table.update().where(table.c.material_id == material_id).values(
            
            content_id=args['content_id'],
            material_title=args['material_title'],
            description=args['description'],
            material_url=args['material_url'],
            created_at=args['created_at']



            )
            session.execute(stmt)
            session.commit()
            return {material_id: args}, 200
        else:
        

            # Insert a new instructor
            stmt = table.insert().values(

            content_id=args['content_id'],
            material_title=args['material_title'],
            description=args['description'],
            material_url=args['material_url'],
            created_at=args['created_at']

            )
            session.execute(stmt)
            session.commit()
            return {material_id: args}, 201

    def delete(self, material_id):

        stmt = table.delete().where(table.c.material_id == material_id)
        session.execute(stmt)
        session.commit()
        return '', 204
