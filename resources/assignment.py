from flask import jsonify, request

from tables import AssignmentScore
from tables import Assignment as table
from tables import User


from setup import APP, SESSION
from datetime import datetime



# resource class
class AssignmentResource():

    @APP.route('/assignment', methods=['GET'])
    def get_all_assignment():


        result = SESSION.query(table).all()


        output = []

        for item in result:
            print(item)

            item_data = {

                "id": item.id,
                "assignment_title": item.assignment_title,
                "content_id": item.content_id,
                "description": item.description,
                "deadline": item.deadline,
                "max_score": item.max_score,
                "grading_criteria": item.grading_criteria,
                "instructions": item.instructions,
                "created_at": item.created_at,
                "submission_format": item.submission_format,
                "updated_at": item.updated_at,
            }

            output.append(item_data)

        return jsonify(output)
    
    @APP.route('/assignment/<id>', methods=['GET'])
    def get_by_id_assignment(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        item_data = {

                "id": item.id,
                "assignment_title": item.assignment_title,
                "content_id": item.content_id,
                "description": item.description,
                "deadline": item.deadline,
                "max_score": item.max_score,
                "grading_criteria": item.grading_criteria,
                "instructions": item.instructions,
                "created_at": item.created_at,
                "submission_format": item.submission_format,
                "updated_at": item.updated_at,
            }


        return jsonify(item_data)
    
    # this route accesses all the scores of a given assignment
    @APP.route('/assignment/<id>/scores', methods=['GET'])
    def get_by_id_assignment_scores(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        output = []

        for i in item.scores:

            # the assignment score object 
            score : AssignmentScore = i

            # the student who tookt the test
            s : User = score.student

            item_data = {

                "score": score.score,
                "submission date": score.submission_date,
                "student id": score.student_id,
                "student name": f"{s.name_given} {s.name_last}",
                "assignment name": item.assignment_title,
                "completed_on_time": (item.deadline >= score.submission_date)
                }
            
            output.append(item_data)

        return jsonify(output)
    

    
    @APP.route('/assignment/<id>', methods=['DELETE'])
    def delete_assignment(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        SESSION.delete(item)
        SESSION.commit()
        
        return jsonify({"message": "user_deleted"})
    
    @APP.route('/assignment/<id>', methods=['PUT'])
    def update_assignment(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()

        q.content_id = data["content_id"]
        q.assignment_title = data["assignment_title"]
        q.description = data["description"]
        q.deadline = data["deadline"]
        q.created_at = datetime().now()
        q.submission_format = data["submission_format"]
        q.updated_at = datetime().now()
        
        SESSION.add(q)
        SESSION.commit()

        return jsonify({"message":"user updated"})
    