from flask import jsonify, request
from tables import Term as table
from setup import APP, SESSION
from sqlalchemy.exc import IntegrityError


from tables import Quiz
from tables import Course
from tables import Content
from tables import Assignment

from decorators import token_required

# resource class
class TermResource():

    # get all terms; intended for tables, indexes, etc. 
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
    
    # gets individual terms by id
    @APP.route('/term/<id>', methods=['GET'])
    def get_by_id_term(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No term by ID"}), 404

        item_data = {
            
            "id":item.id,
            "school_year_start": item.school_year_start,
            "school_year_end": item.school_year_end

            }


        return jsonify(item_data)
    
    # used to create a term object in the database
    # expected format is
    """

    {
        "school_year_start": "yyyy-mm-dd"
        "school_year_end": "yyyy-mm-dd"
    }
    
    """
    @APP.route('/term', methods=['POST'])
    def create_term():

        data = request.get_json()

        q = table()

        q.school_year_start = data['school_year_start']
        q.school_year_end = data['school_year_end']

        try:
            SESSION.add(q)
            SESSION.commit()

        except IntegrityError:

            SESSION.rollback()
            return jsonify({"message": "invalid input - integrity error"})

        return jsonify({"message": "term_created"})
    
    @APP.route('/term/<id>', methods=['DELETE'])
    def delete_term(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No term by ID"}), 404

        SESSION.delete(item)
        SESSION.commit()

        return jsonify({"message": "term_deleted"})
    

    # updates the term; expected format below
    """

    {
        "school_year_start": "yyyy-mm-dd"
        "school_year_end": "yyyy-mm-dd"
    }
    
    """
    @APP.route('/term/<id>', methods=['PUT'])
    def update_term(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()

        q.school_year_start = data['school_year_start']
        q.school_year_end = data['school_year_end']

        SESSION.commit()

        return jsonify({"message":"term updated"})


    # gets the term's quizzes; expected output format below
    @APP.route('/term/<id>/quizzes', methods=['GET'])
    def get_term_quizzes(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()

        if q is None: return jsonify({"message":"no term found"})

        quizzes = q.quizzes

        output = [

        {    
                "id": item.id,
                "content_id": item.content_id,
                "quiz_title": item.quiz_title,
                "quiz_title": item.quiz_title,
                "description": item.description,
                "time_limit": item.time_limit,
                "is_published": item.is_published
        }

        for item in quizzes

        ]

        return jsonify(output)
    

    @APP.route('/term/<id>/assignments', methods=['GET'])
    def get_term_assignments(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()

        if q is None: return jsonify({"message":"no term found"})

        quizzes = q.assignments

        output = [

            {

                "id": item.id,
                "assignment_title": item.assignment_title,
                "content_id": item.content_id,
                "description": item.description,
                "deadline": item.deadline,
                "max_score": item.max_score,
                "grading_criteria": item.grading_criteria,
                "instructions": item.instructions,
                "created_at": item.created_at,
                "submission_format": item.submission_format,
                "updated_at": item.updated_at,
            }

        for item in quizzes

        ]

        return jsonify(output)
    
    @APP.route('/term/<id>/courses', methods=['GET'])
    def get_term_courses(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()

        if q is None: return jsonify({"message":"no term found"})

        courses = q.courses

        output = [

            {

                "id": item.id,
                "course_code": item.course_code,
                "course_name": item.course_name,
                "description": item.description,
                "instructor_id": item.instructor_id,
                "is_published": item.is_published,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
                "term": item.term_id
            }

        for item in courses

        ]

        return jsonify(output)
    

    @APP.route('/term/<id>/content', methods=['GET'])
    def get_term_content_list(id):

        data = request.get_json()

        q = SESSION.query(table).filter(table.id == id).first()

        if q is None: return jsonify({"message":"no term found"})

        content = q.content

        print(content)

        output = [

            {

                "id": item.id,
                "course_id": item.course_id,
                "title": item.title,
                "content_description": item.description,
                "content_url": item.url,
                "created_at": item.created_at,
                "term_id": item.term_id
            }

        for item in content

        ]

        return jsonify(output)