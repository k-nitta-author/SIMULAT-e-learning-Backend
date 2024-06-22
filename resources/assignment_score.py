from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with


# resource class
class AssignmentScore(Resource):

    def __init__(self) -> None:
        super().__init__()

        self.parser = reqparse.RequestParser()

    def get(self, id):
        return {"test": 1}

    def put(self, id):
        args = self.parser.parse_args()

        return {id: args}

    def patch(self):
        pass

    def delete(self):
        pass

