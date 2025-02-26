from flask import jsonify, request
from tables import Quiz as table
from setup import APP, SESSION
from datetime import datetime

from decorators import token_required

# resource class
class QuizResource():

    @APP.route('/quiz', methods=['GET'])
    def get_all_quiz():


        result = SESSION.query(table).order_by(table.id).all()


        output = []

        for item in result:
            item_data = {

                "id": item.id,
                "content_id": item.content_id,
                "term_id": item.term_id,
                "quiz_title": item.quiz_title,
                "quiz_title": item.quiz_title,
                "description": item.description,
                "time_limit": item.time_limit,
                "is_published": item.is_published,

            }

            output.append(item_data)

        return jsonify(output)
    
    @APP.route('/quiz/<id>', methods=['GET'])
    def get_by_id_quiz(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        item_data = {

                "id": item.id,
                "content_id": item.content_id,
                "term_id": item.term_id,
                "quiz_title": item.quiz_title,
                "quiz_title": item.quiz_title,
                "description": item.description,
                "time_limit": item.time_limit,
                "is_published": item.is_published,
            }


        return jsonify(item_data)
    
    @APP.route('/quiz', methods=['POST'])
    def create_quiz():

        data = request.get_json()

        q = table()

        q.content_id = data["content_id"]
        q.term_id = data["term_id"]
        q.quiz_title = data["quiz_title"]
        q.description = data["description"]
        q.time_limit = data["time_limit"]
        q.is_published = False

        
        try:
            SESSION.add(q)
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500

        return jsonify({"message": "user_created"})
    
    @APP.route('/quiz/<id>', methods=['DELETE'])
    def delete_quiz(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        try:
            SESSION.delete(item)
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500

        return jsonify({"message": "user_deleted"})
    
    @APP.route('/quiz/<id>', methods=['PUT'])
    def update_quiz(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()

        q.content_id = data["content_id"]
        q.quiz_title = data["quiz_title"]
        q.term_id = data["term_id"]
        q.description = data["description"]
        q.time_limit = data["time_limit"]
        q.is_published = data["is_published"]
        
        try:
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500
        return jsonify({"message":"user updated"})
    

    @APP.route('/quiz/<id>/publish', methods=['PUT'])
    def publish_quiz(id):

        q = SESSION.query(table).filter(table.id == id).first()

        q.is_published = True
        
        try:
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500
        
        return jsonify({"message":"user updated"})