from flask import jsonify, request
from tables import LessonMaterial as table
from setup import APP, SESSION
from datetime import datetime

from decorators import token_required

# resource class
class LessonMaterialResource():

    @APP.route('/lessons', methods=['GET'])
    def get_all_lesson_material():


        result = SESSION.query(table).all()


        output = []

        for item in result:
            print(item)

            item_data = {

                "content_id": item.content_id,
                "material_title": item.material_title,
                "description": item.description,
                "material_url": item.material_url,
                "created_at": item.created_at,

            }


            output.append(item_data)

        return jsonify(output)
    
    @APP.route('/lessons/<id>', methods=['GET'])
    def get_by_id_lesson_material(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        item_data = {

                "content_id": item.content_id,
                "material_title": item.material_title,
                "description": item.description,
                "material_url": item.material_url,
                "created_at": item.created_at,

            }


        return jsonify(item_data)
    
    @APP.route('/lessons', methods=['POST'])
    def create_lesson_material():

        data = request.get_json()

        q = table()

        q.content_id= data["content_id"]
        q.material_title= data["material_title"]
        q.description= data["description"]
        q.material_url= data["material_url"]
        q.created_at= datetime.now()

        SESSION.add(q)
        SESSION.commit()

        return jsonify({"message": "user_created"})
    
    @APP.route('/lesson_material/<id>', methods=['DELETE'])
    def delete_lesson_material(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        SESSION.delete(item)
        SESSION.commit()
        
        return jsonify({"message": "user_deleted"})
    
    @APP.route('/lesson_material/<id>', methods=['PUT'])
    def update_lesson_material(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()

        q.content_id= data["content_id"]
        q.material_title= data["material_title"]
        q.description= data["description"]
        q.material_url= data["material_url"]
        
        SESSION.add(q)
        SESSION.commit()

        return jsonify({"message":"user updated"})
    