from flask import jsonify, request

from tables import StudyGroupMembership as table
from tables import User, StudyGroup


from setup import APP, SESSION
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from decorators import token_required

# resource class
class AssignmentResource():

    @APP.route('/studygroup/mem', methods=['GET'])
    def get_all_studygroup_memberships():
        result = SESSION.query(table).order_by("student_id").all()
        output = []

        for item in result:
            student = item.member
            study_group = item.study_group
            item_data = {
                "is_leader": item.is_leader,
                "join_date": item.join_date,
                "student_id": item.student_id,
                "student": {
                    "name": f"{student.name_given} {student.name_last}",
                    "email": student.email
                },
                "study_group": {
                    "id": study_group.id,
                    "name": study_group.name,
                    "course_id": study_group.course_id,
                    "max_members": study_group.max_members
                }
            }
            output.append(item_data)

        return jsonify(output)
    
    @APP.route('/studygroup/<id>/join', methods=['POST'])
    def join_studygroup(id):
        data = request.get_json()

        study_group = SESSION.query(StudyGroup).filter(StudyGroup.id == id).first()
        if not study_group:
            return jsonify({"message": "Study group not found"}), 404

        # Check if group is full
        if len(study_group.memberships) >= study_group.max_members:
            return jsonify({"message": "Study group is full"}), 400

        q = table()
        q.is_leader = data["is_leader"]
        q.join_date = datetime.now()
        q.study_group_id = study_group.id
        q.student_id = data["student_id"]

        try:
            SESSION.add(q)
            SESSION.commit()

        except IntegrityError:
            SESSION.rollback()
            return jsonify({"message": "User already in group or invalid input"}), 400

        return jsonify({"message": "Successfully joined study group"}), 201
    
    @APP.route('/studygroup/<id>/quit', methods=['DELETE'])
    def delete_bulletin(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        SESSION.delete(item)
        SESSION.commit()
        
        return jsonify({"message": "studygroup_deleted"})