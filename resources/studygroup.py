from flask import jsonify, request

from tables import StudyGroup as table
from tables import User, StudyGroupMembership

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
        try:
            data = request.get_json()
            q = table()
            
            q.course_id = int(data["course_id"])
            q.max_members = int(data["max_members"])
            q.name = str(data["name"])

            SESSION.add(q)
            SESSION.commit()
            return jsonify({"message": "studygroup_created"}), 201

        except (ValueError, KeyError) as e:
            SESSION.rollback()
            return jsonify({"message": "Invalid input - type conversion error", "error": str(e)}), 400
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500
    
    @APP.route('/studygroup/<id>', methods=['DELETE'])
    def delete_studygroup(id):

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
        try:
            data = request.get_json()
            q = SESSION.query(table).filter(table.id == id).first()
            
            if not q:
                return jsonify({"message": "Study group not found"}), 404

            if "course_id" in data:
                q.course_id = int(data["course_id"])
            if "max_members" in data:
                q.max_members = int(data["max_members"])
            if "name" in data:
                q.name = str(data["name"])

            SESSION.commit()
            return jsonify({"message": "studygroup updated"})

        except (ValueError, KeyError) as e:
            SESSION.rollback()
            return jsonify({"message": "Invalid input - type conversion error", "error": str(e)}), 400
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500
        
        

    @APP.route('/studygroup/<id>/join', methods=['POST'])
    @token_required
    def join_studygroup(current_user, id):
        try:
            # Check if user is a student
            if not current_user.is_student:
                return jsonify({"message": "Only students can join study groups"}), 403

            # Get the study group
            study_group = SESSION.query(table).filter(table.id == id).first()
            if not study_group:
                return jsonify({"message": "Study group not found"}), 404

            # Check if group is full
            if len(study_group.memberships) >= study_group.max_members:
                return jsonify({"message": "Study group is full"}), 400

            # Check if user is already a member
            existing_membership = SESSION.query(StudyGroupMembership).filter_by(
                student_id=current_user.id,
                study_group_id=id
            ).first()
            if existing_membership:
                return jsonify({"message": "Already a member of this study group"}), 400

            # Create new membership
            new_membership = StudyGroupMembership(
                student_id=current_user.id,
                study_group_id=id,
                join_date=datetime.now().date(),
                is_leader=False  # New members are not leaders by default
            )

            SESSION.add(new_membership)
            SESSION.commit()
            return jsonify({"message": "Successfully joined study group"}), 201

        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500

    @APP.route('/studygroup/<id>/members', methods=['GET'])
    def get_studygroup_members(id):
        try:
            study_group = SESSION.query(table).filter(table.id == id).first()
            if not study_group:
                return jsonify({"message": "Study group not found"}), 404

            members = []
            for membership in study_group.memberships:
                members.append({
                    "student_id": str(membership.student_id),
                    "name": f"{membership.member.name_given} {membership.member.name_last}",
                    "is_leader": bool(membership.is_leader)
                })

            return jsonify(members)
        except Exception as e:
            return jsonify({"message": "Error occurred", "error": str(e)}), 500