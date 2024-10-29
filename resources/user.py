from flask import jsonify, request
from tables import User as table
from sqlalchemy.exc import IntegrityError, PendingRollbackError

from tables import Quiz
from tables import QuizScore
from tables import DailyChallengeScore
from tables import AssignmentScore
from tables import StudyGroup
from tables import Course
from tables import Gender
from tables import Badge

from setup import APP, SESSION
from decorators import token_required

from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash
import jwt


# resource class
class UserResource():

    # get all users
    # intended for lists and tables with detailed data
    # CONSIDER: putting behind admin access?
    @APP.route('/user', methods=['GET'])
    def get_all():

        result = SESSION.query(table).all()

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
                "is_super_admin": item.is_super_admin,
                "is_student": item.is_student,
                "is_instructor": item.is_instructor,
                "progress_score": item.progress_score,
                "gender": item.gender
            }

            output.append(item_data)

        return jsonify(output)
    

    # get individual users
    # intended for user profile pages, etc. 
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
                "is_super_admin": item.is_super_admin,
                "is_student": item.is_student,
                "is_instructor": item.is_instructor,
                "progress_score": item.progress_score,
                "gender": item.gender
            }


        return jsonify(item_data)
    
    # gets all instructors
    # intended for lists, tables, etc. 
    # CONSIDER: including informaiton on which class they teach if any
    @APP.route('/user/instructors', methods=['GET'])
    def get_instructors():

        result = SESSION.query(table).filter(table.is_instructor == True).all()

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
                "is_super_admin": item.is_super_admin,
                "is_student": item.is_student,
                "is_instructor": item.is_instructor,
                "progress_score": item.progress_score,
                "gender": item.gender
            }

            output.append(item_data)

        return jsonify(output)
    
    # get detailed list of students
    # CONSIDER: adding details on which courses they are enrolled in
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
                "is_super_admin": item.is_super_admin,
                "is_student": item.is_student,
                "is_instructor": item.is_instructor,
                "progress_score": item.progress_score,
                "gender": item.gender
            }

            output.append(item_data)


        return jsonify(output)
    
    # simply gets the student and returns a list of the badges they have earned. 
    # it is technically possible for a teacher or admin to earn points and badges
    # not pertienent to change tho
    @APP.route('/user/<id>/badges', methods=['GET'])
    def get_student_badges(id):

        student: table = SESSION.query(table).filter(table.id == id).first()

        badges : list = Badge.get_student_badges(SESSION, student)
        
        return jsonify({f"{student.name_given} {student.name_last}": badges})
    
    # gets all admin-level users, nothign more
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
                "is_super_admin": item.is_super_admin,
                "is_student": item.is_student,
                "is_instructor": item.is_instructor,
                "progress_score": item.progress_score,
                "gender": item.gender
            }

            output.append(item_data)


        return jsonify(output)
    
    # allows one to create a new user
    @APP.route('/user', methods=['POST'])
    def create():

        data = request.get_json()

        u = table()

        u.email = data["email"]
        u.is_admin = False
        u.is_instructor = False
        u.is_student = False
        u.is_super_admin = False
        u.password = generate_password_hash(data["password"], method='pbkdf2:sha256')
        u.username = data["username"]
        u.name_given= data["name_given"]
        u.name_last = data["name_last"]
        u.gender = data["gender"]
        u.progress_score = 0
        u.active = True
        
        # simple error handling code; meant to rollback session
        # in case of invalid calls to db
        # do not modify unless one has anything better.
        try:
            SESSION.add(u)
            SESSION.commit()

        except IntegrityError:

            SESSION.rollback()
            return jsonify({"message": "invalid input - integrity error"})
        
        except PendingRollbackError:
            
            SESSION.rollback()

            return jsonify({"message": "invalid input - PendingRollbackError"})

        return jsonify({"message": "user_created"})
    

    # allows one to delete a user
    # requires token with admin-level priveliges
    # TODO: consider further security policies
    @APP.route('/user/<id>', methods=['DELETE'])
    @token_required("admin")
    def delete(id):

        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        item.active = False

        SESSION.add(item)
        SESSION.commit()

        return jsonify({"message": "user_deleted"})
    
    # allows one to update user data
    # intended for use in user profiles in edit mode
    # TODO: consider further changes
    @APP.route('/user/<id>', methods=['PUT'])
    def update(id):

        data = request.get_json()

        u = SESSION.query(table).filter(table.id == id).first()

        u.email = data["email"]
        u.password = generate_password_hash(data["password"], method='pbkdf2:sha256')
        u.username = data["username"]
        u.name_given= data["name_given"]
        u.name_last = data["name_last"]
        
        SESSION.add(u)
        SESSION.commit()

        return jsonify({"message":"user updated"})
    
    # grants or takes away user priveliges to users
    # requires admin level access before proceeding
    @APP.route('/user/<id>/grant', methods=['PUT'])
    @token_required("admin")
    def grant_priveliges_user(id):

        data = request.get_json()

        u = SESSION.query(table).filter(table.id == id).first()

        u.is_admin = data["is_admin"]
        u.is_instructor = data["is_instructor"]
        u.is_student = data["is_student"]
        u.is_super_admin = data["is_super_admin"]
        
        SESSION.add(u)
        SESSION.commit()

        return jsonify({"message":"user updated"})
    
    # gets the user's quiz scores if they have any
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
    
    # gets the user's scores for the challenges
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
    

    # gets the study groups that a user is enrolled into
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

    @APP.route('/user/login', methods=['GET'])
    def login():

        auth = request.authorization

        if auth is None: return jsonify({"message": "no user credentials"}), 401 

        params = auth.parameters

        username  = params.get('username')
        password  = params.get('password')

        u, can_login = table.check_login_credentials(SESSION, username, password)

        if can_login:
            token = jwt.encode({
                'user': u.username,
                'exp': datetime.now() + timedelta(seconds=10),
                'roles': table.get_roles_list(u)}, APP.secret_key)

            return token
        
        return jsonify({"message": "invalid user credentials"})