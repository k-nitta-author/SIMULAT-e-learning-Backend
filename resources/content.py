from flask import jsonify, request
from tables import Content as table
from main import APP, SESSION
from datetime import datetime


from decorators import token_required

# resource class
class ContentResource():

    @APP.route('/content', methods=['GET'])
    def get_all_content():

        result = SESSION.query(table).order_by(table.id).all()

        output = []

        for item in result:
            print(item)

            item_data = {

                "id": item.id,
                "course_id": item.course_id,
                "content_title": item.title,
                "content_description": item.description,
                "content_url": item.url,
                "created_at": item.created_at,
            }


            output.append(item_data)

        return jsonify(output)
    

    # 
    @APP.route('/content/<id>', methods=['GET'])
    def get_by_id_content(id):
        item = SESSION.query(table).filter(table.id == id).first()
        if not item:
            return jsonify({"Message": "No content by ID"}), 404

        # Basic content attributes
        item_data = {
            "id": item.id,
            "type": item.type,
            "title": item.title,
            "description": item.description,
            "url": item.url,
            "created_at": item.created_at,
            "course_id": item.course_id,
            "term_id": item.term_id
        }
        # Include related lesson materials
        item_data["lesson_materials"] = [
            {
                "id": lm.id,
                "material_title": lm.material_title,
                "description": lm.description,
                "material_url": lm.material_url,
                "created_at": lm.created_at
            }
            for lm in item.lesson_materials
        ]
        # Include related course details (if available)
        if item.courses:
            course = item.courses
            item_data["course"] = {
                "id": course.id,
                "course_code": course.course_code,
                "course_name": course.course_name,
                "description": course.description,
                "created_at": course.created_at,
                "updated_at": course.updated_at
            }
        else:
            item_data["course"] = None
        # Include related term details (if available)
        if item.term:
            term = item.term
            item_data["term"] = {
                "id": term.id,
                "school_year_start": term.school_year_start,
                "school_year_end": term.school_year_end
            }
        else:
            item_data["term"] = None

        return jsonify(item_data)
    
    @APP.route('/content', methods=['POST'])
    def create_content():

        data = request.get_json()

        q = table()

        q.course_id = data["course_id"]
        q.title = data["title"]
        q.description = data["description"]
        q.url = data["url"]
        q.created_at = datetime.now()
        q.term_id = data["term_id"]
        q.type =  data["type"]
        
        try:
            SESSION.add(q)
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500

        return jsonify({"message": "content_created"}), 201
    
    @APP.route('/content/<id>', methods=['DELETE'])
    def delete_content(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        try:
            SESSION.delete(item)
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500

        return jsonify({"message": "content_deleted"})
    
    @APP.route('/content/<id>', methods=['PUT'])
    def update_content(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()

        q.course_id = data["course_id"]
        q.content_title = data["title"]
        q.content_description = data["description"]
        q.content_url = data["url"]
        q.created_at = data["created_at"]
        q.term_id = data["term_id"]

        try:
            SESSION.add(q)
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500

        return jsonify({"message":"content updated"})
