from flask import jsonify, request
from tables import User as table

from tables import Quiz
from tables import QuizScore
from tables import DailyChallengeScore
from tables import AssignmentScore
from tables import StudyGroup
from tables import Course

from setup import APP, SESSION

# resource class
class UserResource():

    @APP.route('/user', methods=['GET'])
    def get_all():


        result = SESSION.query(table).all()


        output = []

        for item in result:
            print(item)

            item_data = {

                "id": item.id,
                "name_given": item.name_given,
                "name_last": item.name_given,
                "email": item.email,
                "username": item.username,
                "password": item.password,
                "username": item.username,
                "is_admin": item.is_admin,
                "is_student": item.is_student,
                "is_instructor": item.is_instructor,
            }

            output.append(item_data)

        return jsonify(output)
    
    @APP.route('/user/<id>', methods=['GET'])
    def get_by_id(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        item_data = {

                "id": item.id,
                "name_given": item.name_given,
                "name_last": item.name_given,
                "email": item.email,
                "username": item.username,
                "password": item.password,
                "username": item.username,
                "is_admin": item.is_admin,
                "is_student": item.is_student,
                "is_instructor": item.is_instructor,
            }


        return jsonify(item_data)
    
    @APP.route('/user/instructors', methods=['GET'])
    def get_instructors():

        result = SESSION.query(table).filter(table.is_instructor == True).all()

        output = []

        for item in result:
            print(item)

            item_data = {

                "id": item.id,
                "name_given": item.name_given,
                "name_last": item.name_given,
                "email": item.email,
                "username": item.username,
                "password": item.password,
                "username": item.username,
                "is_admin": item.is_admin,
                "is_student": item.is_student,
                "is_instructor": item.is_instructor,
            }

            output.append(item_data)

        return jsonify(output)
    
    @APP.route('/user/students', methods=['GET'])
    def get_students():

        result = SESSION.query(table).filter(table.is_student == True).all()

        output = []

        for item in result:

            item_data = {

                "id": item.id,
                "name_given": item.name_given,
                "name_last": item.name_given,
                "email": item.email,
                "username": item.username,
                "password": item.password,
                "username": item.username,
                "is_admin": item.is_admin,
                "is_student": item.is_student,
                "is_instructor": item.is_instructor,
            }

            output.append(item_data)


        return jsonify(output)
    
    @APP.route('/user/admin', methods=['GET'])
    def get_admin():

        result = SESSION.query(table).filter(table.is_admin == True).all()

        output = []

        for item in result:

            item_data = {

                "id": item.id,
                "name_given": item.name_given,
                "name_last": item.name_given,
                "email": item.email,
                "username": item.username,
                "password": item.password,
                "username": item.username,
                "is_admin": item.is_admin,
                "is_student": item.is_student,
                "is_instructor": item.is_instructor,
            }

            output.append(item_data)


        return jsonify(output)
    
    @APP.route('/user', methods=['POST'])
    def create():

        data = request.get_json()

        u = table()

        u.email = data["email"]
        u.is_admin = False
        u.is_instructor = False
        u.is_student = False
        u.password = data["password"]
        u.username = data["username"]
        u.name_given= data["name_given"]
        u.name_last = data["name_last"]
        
        SESSION.add(u)
        SESSION.commit()

        return jsonify({"message": "user_created"})
    
    @APP.route('/user/<id>', methods=['DELETE'])
    def delete(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        SESSION.delete(item)
        SESSION.commit()

        

        return jsonify({"message": "user_deleted"})
    
    @APP.route('/user/<id>', methods=['PUT'])
    def update(id):

        data = request.get_json()

        u = SESSION.query(table).filter(table.id == id).first()

        u.email = data["email"]
        u.is_admin = False
        u.is_instructor = False
        u.is_student = False
        u.password = data["password"]
        u.username = data["username"]
        u.name_given= data["name_given"]
        u.name_last = data["name_last"]
        
        SESSION.add(u)
        SESSION.commit()

        return jsonify({"message":"user updated"})
    

    
    @APP.route('/user/<id>/q/scores', methods=['GET'])
    def get_user_quiz_scores(id):

        u = SESSION.query(table).filter(table.id == id).first()

        output = []

        scores = u.quiz_scores

        for item in scores:

            score: QuizScore = item

            score_data = {
                "submission date": score.submission_date,
                "student ID": score.student_id,
                "Quiz ID": score.quiz_id,
                "Score": score.score
            }

            output.append(score_data)



        return jsonify({"message":output})
    
    @APP.route('/user/<id>/c/scores', methods=['GET'])
    def get_user_challenge_scores(id):

        u = SESSION.query(table).filter(table.id == id).first()

        output = []

        scores = u.challenge_scores

        for item in scores:

            score: DailyChallengeScore = item
            
            score_data = {
                "submission date":score.submission_date,
                "Score": score.score
            }

            output.append(score_data)

        return jsonify({"message":output})
    

    @APP.route('/user/<id>/studygroups/', methods=['GET'])
    def get_user_study_groups(id):

        u = SESSION.query(table).filter(table.id == id).first()

        output = []

        study_groups = u.study_groups_membership

        for item in study_groups:

            study_group: StudyGroup = item.study_group
            course: Course = study_group.course
            
            study_group_data = {
                "Study Group Name":study_group.name,
                "study group id":study_group.id,
                "course id": course.id,
                "course name": course.course_name,
            }

            output.append(study_group_data)

        return jsonify({"message":output})

    @APP.route('/user/<id>/a/scores', methods=['GET'])
    def get_user_assignment_scores(id):

        u = SESSION.query(table).filter(table.id == id).first()

        output = []

        scores = u.assignment_scores

        for item in scores:

            score: AssignmentScore = item
            
            score_data = {
                "Score": score.score,
                "Submission Date": score.submission_date
            }

            output.append(score_data)



        return jsonify({"message":output})