from flask import jsonify, request
from tables import Content as table
from setup import APP, SESSION
from datetime import datetime


from decorators import token_required

# resource class
class ContentResource():

    @APP.route('/content', methods=['GET'])
    def get_all_content():

        result = SESSION.query(table).order_by(id).all()

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
    
    @APP.route('/content/<id>', methods=['GET'])
    def get_by_id_content(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        item_data = {

                "id": item.id,
                "course_id": item.course_id,
                "content_title": item.title,
                "content_description": item.description,
                "content_url": item.url,
                "created_at": item.created_at,
            }


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
