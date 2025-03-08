from flask import jsonify, request
from tables import Course as table
from tables import User
from setup import APP, SESSION

from sqlalchemy.exc import IntegrityError

from datetime import datetime

from decorators import token_required

# resource class
class CourseResource():

    # this route accesses all the courses

    @APP.route('/course', methods=['GET'])
    def course_get_all():
        result = SESSION.query(table).order_by(table.id).all()

        print(result)


        output = []

        for item in result:
            print(item)

            item_data = {

                "id": item.id,
                "course_code": item.course_code,
                "course_name": item.course_name,
                "description": item.description,
                "instructor_id": item.instructor_id,
                "is_published": item.is_published,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
                "term": item.term_id,
                "instructor": f"{item.instructor.name_given} {item.instructor.name_last}"
            }

            output.append(item_data)

        return jsonify(output)

    # this route accesses a specific course
    @APP.route('/course/<id>', methods=['GET'])
    def course_get_by_id(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No Course by ID"}), 404

        item_data = {

                "id": item.id,
                "course_code": item.course_code,
                "course_name": item.course_name,
                "description": item.description,
                "instructor_id": item.instructor_id,
                "is_published": item.is_published,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
                "instructor": f"{item.instructor.name_given} {item.instructor.name_last}",
                "term": item.term_id,
                "content_list": [{"id": c.id, "title": c.title, "url": c.url} for c in item.content_list],
                "enrollments": [{"course_id": ce.course_id, "user_id": ce.user_id, "enroll_date": ce.enroll_date} for ce in item.enrollments],
                "study_groups": [{"id": sg.id, "name": sg.name, "course_id": sg.course_id, "max_members": sg.max_members} for sg in item.study_groups]
            }


        return jsonify(item_data)


    # this route creates a course
    @APP.route('/course', methods=['POST'])
    def course_create():

        data = request.get_json()

        c = table()

        c.course_code = data["course_code"]
        c.course_name = data["course_name"]
        c.description = data["description"]
        c.instructor_id = data["instructor_id"]
        c.is_published = False
        c.created_at = datetime.now()
        c.updated_at = datetime.now()
        c.term_id = data["term_id"]

        try:
            SESSION.add(c)
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500

        return jsonify({"message": "course_created"}), 201
    
    # this route deletes a course
    @APP.route('/course/<id>', methods=['DELETE'])
    def course_delete(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No Course by ID"}), 404

        try:
            SESSION.delete(item)
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500

        return jsonify({"message": "course_deleted"})
    
    # this route updates a course
    @APP.route('/course/<id>', methods=['PUT'])
    def course_update(id):


        data = request.get_json()

        c = SESSION.query(table).filter(table.id == id).first()

        c.course_code = data["course_code"]
        c.course_name = data["course_name"]
        c.description = data["description"]
        c.instructor_id = data["instructor_id"]
        c.is_published= data["is_published"]
        c.updated_at = datetime.now()

        try:        
            SESSION.add(c)
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message":"something went wrong", "error": str(e)}), 500

        return jsonify({"message":"course updated"})
