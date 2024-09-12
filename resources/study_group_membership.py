from flask import jsonify, request

from tables import StudyGroupMembership as table
from tables import User, StudyGroup


from setup import APP, SESSION
from datetime import datetime

from sqlalchemy.exc import IntegrityError


# resource class
class AssignmentResource():

    @APP.route('/studygroup/mem', methods=['GET'])
    def get_all_studygroup_memberships():


        result = SESSION.query(table).all()

        output = []

        for item in result:
            print(item)

            item_data = {

                "is_leader":item.is_leader,
                "join_date":item.join_date,
                "student_id":item.student_id
            }

            output.append(item_data)

        return jsonify(output)
    
    @APP.route('/studygroup/<id>/join', methods=['POST'])
    def join_studygroup(id):

        data = request.get_json()

        q = table()

        study_group = SESSION.query(StudyGroup).filter(StudyGroup.id == id).first()

        q.is_leader = data["is_leader"]
        q.join_date = datetime.now()
        q.study_group_id = study_group.id
        q.student_id = data["student_id"]

        try:
            SESSION.add(q)
            SESSION.commit()

        except IntegrityError:

            SESSION.rollback()
            return jsonify({"message": "invalid input - integrity error"})

        return jsonify({"message": "user_created"})
    
    @APP.route('/studygroup/<id>/quit', methods=['DELETE'])
    def delete_bulletin(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        SESSION.delete(item)
        SESSION.commit()
        
        return jsonify({"message": "studygroup_deleted"})