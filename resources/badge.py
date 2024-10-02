from flask import jsonify, request
from tables import Badge as table
from setup import APP, SESSION
from datetime import datetime

from decorators import token_required

# resource class
class BadgeResource():

    @APP.route('/badge', methods=['GET'])
    def get_all_badge():

        result = SESSION.query(table).all()

        output = []

        for item in result:
            item_data = {

                "id": item.id,
                "name": item.name,
                "description":item.description,
                "pts_required":item.pts_required

            }

            output.append(item_data)

        return jsonify(output)
    
    @APP.route('/quiz/<id>', methods=['GET'])
    def get_by_id_badge(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No badge by ID"}), 404

        item_data = {

                "id": item.id,
                "name": item.name,
                "description":item.description,
                "pts_required":item.pts_required

            }


        return jsonify(item_data)
    
    @APP.route('/badge', methods=['POST'])
    def create_badge():

        data = request.get_json()

        q = table()

        q.description = data["description"]
        q.name = data["name"]
        q.pts_required = data["pts_required"]

        SESSION.add(q)
        SESSION.commit()

        return jsonify({"message": "badge_created"})
    
    @APP.route('/badge/<id>', methods=['DELETE'])
    def delete_badge(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No badge by ID"}), 404

        SESSION.delete(item)
        SESSION.commit()

        return jsonify({"message": "badge_deleted"})
    
    @APP.route('/badge/<id>', methods=['PUT'])
    def update_badge(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()
        
        q.description = data["description"]
        q.name = data["name"]
        q.pts_required = data["pts_required"]

        SESSION.commit()

        return jsonify({"message":"badge updated"})
    

