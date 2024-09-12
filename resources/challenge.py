from flask import jsonify, request
from tables import DailyChallenge as table
from setup import APP, SESSION
from datetime import datetime


from sqlalchemy.exc import IntegrityError, PendingRollbackError

# resource class
class DailyChallengeResource():

    @APP.route('/challenge', methods=['GET'])
    def get_all_challenge():

        result = SESSION.query(table).all()

        output = []

        for item in result:
            print(item)

            item_data = {
                 
            "id": item.id,
            "content_id": item.content_id,
            "publication_date": item.publication_date,
            "is_published": item.is_published,
            "created_at": item.created_at,
            "updated_at": item.updated_at

            }
            output.append(item_data)

        return jsonify(output)
    
    @APP.route('/challenge/<id>', methods=['GET'])
    def get_by_id_challenge(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        item_data = {

            "id": item.id,
            "content_id": item.content_id,
            "publication_date": item.publication_date,
            "is_published": item.is_published,
            "created_at": item.created_at,
            "updated_at": item.updated_at
            }


        return jsonify(item_data)
    
    @APP.route('/challenge', methods=['POST'])
    def create_challenge():

        data = request.get_json()

        q = table()

        q.content_id = data["content_id"]
        q.publication_date= datetime.now()
        q.is_published= data["is_published"]
        q.created_at= datetime.now()
        q.updated_at= datetime.now()
        

        try:
            SESSION.add(q)
            SESSION.commit()

        except IntegrityError:

            SESSION.rollback()
            return jsonify({"message": "invalid input - integrity error"})

        return jsonify({"message": "user_created"})
    
    @APP.route('/challenge/<id>', methods=['DELETE'])
    def delete_challenge(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        SESSION.delete(item)
        SESSION.commit()
        
        return jsonify({"message": "user_deleted"})
    
    @APP.route('/challenge/<id>', methods=['PUT'])
    def update_challenge(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()

        q.content_id = data["content_id"]
        q.publication_date= data["publication_date"]
        q.is_published= data["is_published"]
        q.updated_at= datetime.now()
        
        SESSION.add(q)
        SESSION.commit()

        return jsonify({"message":"user updated"})
    