from flask import jsonify, request
from tables import Term as table
from setup import APP, SESSION

from decorators import token_required

# resource class
class TermResource():

    @APP.route('/term', methods=['GET'])
    def get_all_term():

        result = SESSION.query(table).all()

        output = []

        for item in result:
            item_data = {

                "id":item.id,
                "school_year_start": item.school_year_start,
                "school_year_end": item.school_year_end


            }

            output.append(item_data)

        return jsonify(output)
    
    @APP.route('/term/<id>', methods=['GET'])
    def get_by_term(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No term by ID"}), 404

        item_data = {
            
            "id":item.id,
            "school_year_start": item.school_year_start,
            "school_year_end": item.school_year_end

            }


        return jsonify(item_data)
    
    @APP.route('/term', methods=['POST'])
    def create_term():

        data = request.get_json()

        q = table()

        q.school_year_start = data['school_year_start']
        q.school_year_end = data['school_year_end']

        SESSION.add(q)
        SESSION.commit()

        return jsonify({"message": "term_created"})
    
    @APP.route('/term/<id>', methods=['DELETE'])
    def delete_term(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No term by ID"}), 404

        SESSION.delete(item)
        SESSION.commit()

        return jsonify({"message": "term_deleted"})
    
    @APP.route('/term/<id>', methods=['PUT'])
    def update_term(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()

        q.school_year_start = data['school_year_start']
        q.school_year_end = data['school_year_end']

        SESSION.commit()

        return jsonify({"message":"term updated"})
    

