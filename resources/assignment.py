from flask import jsonify, request

from tables import AssignmentScore
from tables import Assignment as table
from tables import User

from setup import APP, SESSION
from datetime import datetime

from decorators import token_required

# resource class
class AssignmentResource():

    @APP.route('/assignment', methods=['GET'])
    def get_all_assignment():

        result = SESSION.query(table).order_by(table.id).all()

        output = []

        for item in result:

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
                "term_id": item.term_id,
                "term": {
                    "id": item.term.id,
                    "school_year_start": item.term.school_year_start,
                    "school_year_end": item.term.school_year_end,
                },
                "scores": [
                    {
                        "score": score.score,
                        "submission_date": score.submission_date,
                        "student_id": score.student_id,
                        "student_name": f"{score.student.name_given} {score.student.name_last}"
                    } for score in item.scores
                ]

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
                "submission_date": score.submission_date,
                "student_id": score.student_id,
                "student_name": f"{s.name_given} {s.name_last}",
                "assignment_name": item.assignment_title,
                "completed_on_time": (item.deadline >= score.submission_date)
                }
            
            output.append(item_data)

        return jsonify(output)
    
    @APP.route('/assignment/<id>', methods=['DELETE'])
    def delete_assignment(id):
        item = SESSION.query(table).filter(table.id == id).first()
        if not item:
            return jsonify({"Message": "No assignment by ID"}), 404
        try:
            SESSION.delete(item)
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500
        return jsonify({"message": "assignment_deleted"})
    
    @APP.route('/assignment/<id>', methods=['PUT'])
    def update_assignment(id):
        data = request.get_json()
        a = SESSION.query(table).filter(table.id == id).first()
        if not a:
            return jsonify({"message": "No assignment by ID"}), 404

        a.assignment_title = data.get("assignment_title", a.assignment_title)
        a.content_id = data.get("content_id", a.content_id)
        a.description = data.get("description", a.description)
        a.deadline = datetime.strptime(data["deadline"], "%a, %d %b %Y %H:%M:%S %Z") if "deadline" in data else a.deadline
        a.grading_criteria = data.get("grading_criteria", a.grading_criteria)
        a.instructions = data.get("instructions", a.instructions)
        a.max_score = data.get("max_score", a.max_score)
        a.submission_format = data.get("submission_format", a.submission_format)
        a.updated_at = datetime.now()

        try:
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500
        return jsonify({"message": "assignment updated"})

    @APP.route('/assignment', methods=['POST'])
    def create_assignment():
        data = request.get_json()
        new_assignment = table(
            assignment_title=data["assignment_title"],
            content_id=data["content_id"],
            created_at= datetime.now(),
            deadline=datetime.strptime(data["deadline"], "%a, %d %b %Y %H:%M:%S %Z"),
            description=data["description"],
            grading_criteria=data["grading_criteria"],
            id=data["id"],
            instructions=data["instructions"],
            max_score=data["max_score"],
            submission_format=data["submission_format"],
            updated_at=datetime.now()
        )
        try:
            SESSION.add(new_assignment)
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500
        return jsonify({"message": "assignment created", "assignment": data}), 201
