from flask import jsonify, request
from tables import DailyChallengeScore as table
from setup import APP, SESSION
from datetime import datetime

from sqlalchemy.exc import IntegrityError

# resource class
class DailyChallengeScoreResource():
    
    @APP.route('/challenge/<challenge_id>/score', methods=['GET'])
    def get_by_challenge_challenge_score(challenge_id):

        result = SESSION.query(table).filter(table.challenge_id == challenge_id).all()

        if not result: return jsonify({"Message":"No User by ID"}), 404


        output = []

        for item in result:

            item_data = {

                "score": item.score,
                "submission_date": item.submission_date,
                "challenge_id": item.challenge_id,
                "user_id": item.user_id
            }

        output.append(item_data)


        return jsonify(output)
    
    @APP.route('/challenge/u/<user_id>/score', methods=['GET'])
    def get_by_user_challenge_score(user_id):

        result = SESSION.query(table).filter(table.user_id == user_id).all()

        if not result: return jsonify({"Message":"No User by ID"}), 404


        output = []

        for item in result:

            item_data = {

                "score": item.score,
                "submission_date": item.submission_date,
                "challenge_id": item.challenge_id,
                "user_id": item.user_id
            }

        output.append(item_data)


        return jsonify(output)
    
    @APP.route('/challenge/<id>/score', methods=['POST'])
    def create_challenge_score(id):

        data = request.get_json()

        q = table()

        q.score= data["score"]
        q.submission_date= datetime.now()
        q.challenge_id= id,
        q.user_id= data["user_id"]
        
        try:
            SESSION.add(q)
            SESSION.commit()

        except IntegrityError:

            SESSION.rollback()
            return jsonify({"message": "invalid input - integrity error"})

        return jsonify({"message": "user_created"})
    
    @APP.route('/challenge/<id>/score', methods=['DELETE'])
    def delete_challenge_score(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        SESSION.delete(item)
        SESSION.commit()
        
        return jsonify({"message": "user_deleted"})
    
    @APP.route('/challenge/<id>/score', methods=['PUT'])
    def update_challenge_score(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()

        q.score= data["score"]
        q.submission_date= datetime.now()
        q.challenge_id= data["challenge_id"],
        q.user_id= data["user_id"]
        
        SESSION.add(q)
        SESSION.commit()

        return jsonify({"message":"user updated"})
    