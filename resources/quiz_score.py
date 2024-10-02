from flask import jsonify, request
from tables import QuizScore as table
from setup import APP, SESSION
from datetime import datetime

from decorators import token_required

# resource class
class QuizScoreResource():

    @APP.route('/user/quiz/scores', methods=['GET'])
    def get_all_quiz_scores():


        result = SESSION.query(table).all()


        output = []

        for item in result:
            print(item)

            item_data = {
                "score": item.score,
                "submission_date": item.submission_date,
                "quiz_id": item.quiz_id,
                "student_id": item.student_id
            }

            output.append(item_data)

        return jsonify(output)
    
    @APP.route('/user/quiz/<id>/score', methods=['GET'])
    def get_by_id_quiz_scores(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        item_data = {
                "score": item.score,
                "submission_date": item.submission_date,
                "quiz_id": item.quiz_id,
                "student_id": item.student_id

            }


        return jsonify(item_data)
    
    @APP.route('/user/quiz/<id>', methods=['POST'])
    def create_quiz_scores():

        data = request.get_json()

        q = table()


        
        SESSION.add(q)
        SESSION.commit()

        return jsonify({"message": "user_created"})
    
    @APP.route('/user/quiz/<id>/score', methods=['PUT'])
    def update_quiz_score(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()

        q.score = data["score"]
        q.submission_date = data["submission_date"]
        q.quiz_id = data["quiz_id"]
        q.student_id = data["student_id"]
        
        SESSION.add(q)
        SESSION.commit()

        return jsonify({"message":"user updated"})
    