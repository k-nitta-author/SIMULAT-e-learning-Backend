from flask import jsonify, request

from tables import BulletinPost as table
from tables import User


from setup import APP, SESSION
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from decorators import token_required


# resource class
class AssignmentResource():

    @APP.route('/bulletin', methods=['GET'])
    def get_all_bulletin():


        result = SESSION.query(table).all()


        output = []

        for item in result:

            item_data = {
                "id": item.id,
                "uid": item.author_uid,
                "description": item.description,
                "name": item.name,
                "is urgent": item.is_urgent,
                "public date": item.publish_date
            }

            output.append(item_data)

        return jsonify(output)
    
    @APP.route('/bulletin/<id>', methods=['GET'])
    def get_by_id_bulletin(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No bulletin by ID"}), 404

        item_data = {
                "id": item.id,
                "uid": item.author_uid,
                "description": item.description,
                "name": item.name,
                "is urgent": item.is_urgent,
                "public date": item.publish_date
            }


        return jsonify(item_data)
    
    @APP.route('/bulletin', methods=['POST'])
    def create_bulletin():

        data = request.get_json()

        q = table()

        q.publish_date = datetime.now()
        q.author_uid = data["author_uid"]
        q.description = data["description"]
        q.is_urgent = data["is_urgent"]
        q.name = data["name"]
        
        

        try:
            SESSION.add(q)
            SESSION.commit()

        except IntegrityError:

            SESSION.rollback()
            return jsonify({"message": "invalid input - integrity error"})

        return jsonify({"message": "user_created"})
    
    @APP.route('/bulletin/<id>', methods=['DELETE'])
    def delete_bulletin(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        SESSION.delete(item)
        SESSION.commit()
        
        return jsonify({"message": "bulletin_deleted"})
    
    @APP.route('/bulletin/<id>', methods=['PUT'])
    def update_bulletin(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()

        q.author_uid = data["author_uid"]
        q.description = data["description"]
        q.is_urgent = data["is_urgent"]
        q.name = data["name"]

        SESSION.add(q)
        SESSION.commit()

        return jsonify({"message":"bulletin updated"})