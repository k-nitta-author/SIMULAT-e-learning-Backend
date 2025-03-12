from flask import jsonify, request

from tables import StudyGroup as table
from tables import User

from setup import APP, SESSION
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from decorators import token_required

# resource class
class StudyGroupResource():

    @APP.route('/studygroup', methods=['GET'])
    def get_all_studygroup():
        try:
            result = SESSION.query(table).order_by(table.id).all()
            output = []

            for item in result:
                course = item.courses
                memberships = []
                for membership in item.memberships:
                    join_date = membership.join_date.isoformat() if membership.join_date else None
                    memberships.append({
                        "student_id": str(membership.student_id),  # Convert to string to ensure serialization
                        "student_name": f"{membership.member.name_given} {membership.member.name_last}",
                        "join_date": join_date,
                        "is_leader": bool(membership.is_leader)  # Ensure boolean type
                    })
                    
                item_data = {
                    "id": str(item.id),  # Convert to string to ensure serialization
                    "course_id": str(item.course_id),
                    "course_name": str(course.course_name),
                    "max_members": int(item.max_members),  # Ensure integer type
                    "name": str(item.name),
                    "memberships": memberships
                }
                output.append(item_data)

            return jsonify(output)
        except Exception as e:
            return jsonify({"message": "Error occurred", "error": str(e)}), 500
    
    @APP.route('/studygroup/<id>', methods=['GET'])
    def get_by_id_studygroup(id):
        try:
            item = SESSION.query(table).filter(table.id == id).first()

            if not item: 
                return jsonify({"Message":"No studygroup by ID"}), 404

            course = item.courses
            memberships = []
            for membership in item.memberships:
                join_date = membership.join_date.isoformat() if membership.join_date else None
                memberships.append({
                    "student_id": str(membership.student_id),
                    "student_name": f"{membership.member.name_given} {membership.member.name_last}",
                    "join_date": join_date,
                    "is_leader": bool(membership.is_leader)
                })

            item_data = {
                "id": str(item.id),
                "course_id": str(item.course_id),
                "course_name": str(course.course_name),
                "max_members": int(item.max_members),
                "name": str(item.name),
                "memberships": memberships
            }

            return jsonify(item_data)
        except Exception as e:
            return jsonify({"message": "Error occurred", "error": str(e)}), 500
    
    @APP.route('/studygroup', methods=['POST'])
    def create_studygroup():

        data = request.get_json()

        q = table()
        
        q.course_id = data["course_id"]
        q.max_members = data["max_members"]
        q.name = data["name"]

        try:
            SESSION.add(q)
            SESSION.commit()

        except Exception as e:

            SESSION.rollback()
            return jsonify({"message": "invalid input", "error": str(e)}), 400

        return jsonify({"message": "studygroup_created"}), 201
    
    @APP.route('/studygroup/<id>', methods=['DELETE'])
    def delete_bulletin(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        try:
            SESSION.delete(item)
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500
        
        return jsonify({"message": "studygroup_deleted"})
    
    @APP.route('/studygroup/<id>', methods=['PUT'])
    def update_studygroup(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()


        try:
            SESSION.add(q)
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500

        return jsonify({"message":"studygroup updated"})