from flask import jsonify, request

from tables import StudyGroup as table
from tables import User


from setup import APP, SESSION
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from decorators import token_required

# resource class
class AssignmentResource():

    @APP.route('/studygroup', methods=['GET'])
    def get_all_studygroup():


        result = SESSION.query(table).all()

        output = []

        for item in result:

            item_data = {

                "id": item.id,
                "course_id": item.course_id,
                "max_members": item.max_members,
                "name": item.name,
            }

            output.append(item_data)

        return jsonify(output)
    
    @APP.route('/studygroup/<id>', methods=['GET'])
    def get_by_id_studygroup(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No studygroup by ID"}), 404

        item_data = {
                "id": item.id,
                "course_id": item.course_id,
                "max_members": item.max_members,
                "name": item.name
        }


        return jsonify(item_data)
    
    @APP.route('/studygroup', methods=['POST'])
    def create_studygroup():

        data = request.get_json()

        q = table()
        
        q.course_id = data["course_id"]
        q.max_members = data["max_members"]
        q.name = data["name"]

        try:
            SESSION.add(q)
            SESSION.commit()

        except IntegrityError:

            SESSION.rollback()
            return jsonify({"message": "invalid input - integrity error"})

        return jsonify({"message": "user_created"})
    
    @APP.route('/studygroup/<id>', methods=['DELETE'])
    def delete_bulletin(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        SESSION.delete(item)
        SESSION.commit()
        
        return jsonify({"message": "studygroup_deleted"})
    
    @APP.route('/studygroup/<id>', methods=['PUT'])
    def update_studygroup(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()


        SESSION.add(q)
        SESSION.commit()

        return jsonify({"message":"studygroup updated"})