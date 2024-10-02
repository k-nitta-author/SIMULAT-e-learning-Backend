from flask import jsonify, request
from tables import AssignmentScore as table
from setup import APP, SESSION
from datetime import datetime
from decorators import token_required

# resource class
class AssignmentScoreResource():

    @APP.route('/assignment/score', methods=['GET'])
    def get_all_assignment_score():

        result = SESSION.query(table).all()
        output = []

        for item in result:
            print(item)

            item_data = {

                "score": item.score,
                "submission_date": item.submission_date,
                "assignment_id": item.assignment_id,
                "student_id": item.student_id,

            }

            output.append(item_data)

        return jsonify(output)
    
    @APP.route('/assignment/<id>/s/<sid>/score', methods=['GET'])
    def get_one_assignment_score(id, sid):

        item = SESSION.query(table).filter(table.assignment_id == id and table.student_id == sid).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        item_data = {

                "score": item.score,
                "submission_date": item.submission_date,
                "assignment_id": item.assignment_id,
                "student_id": item.student_id,
            }
        
        return jsonify(item_data)
    
    @APP.route('/assignment/<id>/s/<sid>/score', methods=['POST'])
    def create_assignment_score(id, sid):

        data = request.get_json()

        q = table()

        q.score = data["score"]
        q.submission_date = data["submission_date"]
        q.assignment_id = id
        q.student_id = sid
        
        SESSION.add(q)
        SESSION.commit()

        return jsonify({"message": "user_created"})
    
    @APP.route('/assignment/<id>/score', methods=['DELETE'])
    def delete_assignment_score(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        SESSION.delete(item)
        SESSION.commit()
        
        return jsonify({"message": "user_deleted"})
    
    @APP.route('/assignment/<id>/score', methods=['PUT'])
    def update_assignment_score(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()

        q.score = data["score"]
        q.submission_date = data["submission_date"]
        q.assignment_id = data["assignment_id"]
        q.student_id = data["student_id"]
        
        SESSION.add(q)
        SESSION.commit()

        return jsonify({"message":"user updated"})
    