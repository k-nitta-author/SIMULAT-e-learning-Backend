from flask import jsonify, request
from tables import Content as table
from setup import APP, SESSION
from datetime import datetime

# resource class
class ContentResource():

    @APP.route('/content', methods=['GET'])
    def get_all_content():

        result = SESSION.query(table).all()

        output = []

        for item in result:
            print(item)

            item_data = {

                "id": item.id,
                "course_id": item.course_id,
                "content_type": item.content_type,
                "content_title": item.content_title,
                "content_description": item.content_description,
                "content_url": item.content_url,
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
                "content_type": item.content_type,
                "content_title": item.content_title,
                "content_description": item.content_description,
                "content_url": item.content_url,
                "created_at": item.created_at,
            }


        return jsonify(item_data)
    
    @APP.route('/content', methods=['POST'])
    def create_content():

        data = request.get_json()

        q = table()

        q.course_id = data["course_id"]
        q.content_type = data["content_type"]
        q.content_title = data["content_title"]
        q.content_description = data["content_description"]
        q.content_url = data["content_url"]
        q.created_at = datetime.now()
        
        SESSION.add(q)
        SESSION.commit()

        return jsonify({"message": "user_created"})
    
    @APP.route('/content/<id>', methods=['DELETE'])
    def delete_content(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        SESSION.delete(item)
        SESSION.commit()

        return jsonify({"message": "user_deleted"})
    
    @APP.route('/content/<id>', methods=['PUT'])
    def update_content(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()

        q.course_id = data["course_id"]
        q.content_type = data["content_type"]
        q.content_title = data["content_title"]
        q.content_description = data["content_description"]
        q.content_url = data["content_url"]
        q.created_at = data["created_at"]

        SESSION.add(q)
        SESSION.commit()

        return jsonify({"message":"user updated"})
    