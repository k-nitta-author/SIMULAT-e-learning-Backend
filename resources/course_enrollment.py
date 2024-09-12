from flask import jsonify, request
from tables import CourseEnrollment as table
from setup import APP, SESSION
from datetime import datetime

# resource class
class CourseEnrollmentResource():

    @APP.route('/user/<user_id>/course', methods=['GET'])
    def get_all_enrollments(user_id):


        result = SESSION.query(table).filter(table.user_id == user_id).all()


        output = []

        for item in result:
            print(item)

            item_data = {

                "enroll_date": item.enroll_date,
                "course_id": item.course_id,
                "user_id": item.user_id,

            }

            output.append(item_data)

        return jsonify(output)
    
    @APP.route('/user/<user_id>/course/<course_id>', methods=['GET'])
    def get_by_id_enrollments(course_id, user_id):

        item = SESSION.query(table).filter(table.course_id == course_id and table.user_id == user_id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        item_data = {

                "enroll_date": item.enroll_date,
                "course_id": item.course_id,
                "user_id": item.user_id,
            }


        return jsonify(item_data)
    
    @APP.route('/user/<user_id>/course/enroll/<course_id>', methods=['POST'])
    def create_enrollments(user_id, course_id):

        q = table()

        q.enroll_date = datetime.now()
        q.course_id = course_id
        q.user_id = user_id

        
        SESSION.add(q)
        SESSION.commit()

        return jsonify({"message": "user_created"})
    
    @APP.route('/user/<user_id>/course/<course_id>', methods=['DELETE'])
    def delete_enrollments(user_id, course_id):

        item = SESSION.query(table).filter(table.user_id == user_id and table.course_id == course_id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        SESSION.delete(item)
        SESSION.commit()

        

        return jsonify({"message": "user_deleted"})
    