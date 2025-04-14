from flask import jsonify, request, session
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
from tables import DailyChallenge
from tables import Assignment
from tables import StudyGroupMembership

from setup import APP, SESSION
from decorators import token_required

from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash
import jwt
import aiohttp

from os import environ


# Environment variables
WEAVY_URL = environ.get("WEAVY_URL")
API_KEY = environ.get("WEAVY_API_KEY")


# Global token store
_token_store: dict[str, str] = {}


def calculate_progress_score(user):
    quiz_total = sum(score.score for score in user.quiz_scores)
    assignment_total = sum(score.score for score in user.assignment_scores)
    challenge_total = sum(score.score for score in user.challenge_scores)
    return quiz_total + assignment_total + challenge_total

# resource class
class UserResource():

    # Helper function to calculate progress score


    # get all users
    # intended for lists and tables with detailed data
    # CONSIDER: putting behind admin access?
    @APP.route('/user', methods=['GET'])
    def get_all():

        result = SESSION.query(table).order_by(table.id).all()

        output = []

        for item in result:

            item_data = {

                "id": item.id,
                "name_given": item.name_given,
                "name_last": item.name_last,
                "email": item.email,
                "username": item.username,
                "password": item.password,
                "username": item.username,
                "is_admin": item.is_admin,
                "is_super_admin": item.is_super_admin,
                "is_student": item.is_student,
                "is_instructor": item.is_instructor,
                "progress_score": calculate_progress_score(item),
                "gender": item.gender,
                "active": item.active
            }

            output.append(item_data)

        return jsonify(output)


    # get individual users
    # intended for user profile pages, etc.
    @APP.route('/user/<id>', methods=['GET'])
    def get_by_id(id):
        try:
            item = SESSION.query(table).filter(table.id == id).first()
        except Exception as e:
            return jsonify({"message": "Error occurred", "error": str(e)}), 500

        if not item:
            return jsonify({"message": "No user by ID"}), 404

        # Calculate course-specific progress scores
        course_progress = []
        for enrollment in item.enrollments:
            course = enrollment.courses
            
            # Get all assessments for this course
            course_quizzes = [qs for qs in item.quiz_scores if qs.quiz.content_id == course.id]
            course_assignments = [asg for asg in item.assignment_scores if asg.assignment.content_id == course.id]
            course_challenges = [cs for cs in item.challenge_scores if cs.challenge.content_id == course.id]
            
            # Calculate total scores earned
            quiz_score = sum(qs.score for qs in course_quizzes)
            assignment_score = sum(asg.score for asg in course_assignments)
            challenge_score = sum(cs.score for cs in course_challenges)
            
            # Calculate maximum possible scores
            max_quiz_score = sum(100 for _ in course_quizzes)  # Assuming quizzes are out of 100
            max_assignment_score = sum(asg.assignment.max_score for asg in course_assignments)  # Fix: access max_score through assignment
            max_challenge_score = sum(100 for _ in course_challenges)  # Assuming challenges are out of 100
            
            # Calculate total percentage
            total_earned = quiz_score + assignment_score + challenge_score
            total_possible = max_quiz_score + max_assignment_score + max_challenge_score
            
            percentage = (total_earned / total_possible * 100) if total_possible > 0 else 0
            
            course_progress.append({
                "course_id": course.id,
                "course_name": course.course_name,
                "course_code": course.course_code,
                "completion_percentage": round(percentage, 2),
                "scores": {
                    "quizzes": quiz_score,
                    "assignments": assignment_score,
                    "challenges": challenge_score
                },
                "total_score": total_earned,
                "max_possible": total_possible
            })

        item_data = {
            "id": item.id,
            "name_given": item.name_given,
            "name_last": item.name_last,
            "email": item.email,
            "username": item.username,
            "password": item.password,
            "is_admin": item.is_admin,
            "is_super_admin": item.is_super_admin,
            "is_student": item.is_student,
            "is_instructor": item.is_instructor,
            "gender": item.gender,
            "overall_progress": calculate_progress_score(item),
            "course_progress": course_progress,
            "active": item.active
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
                "name_last": item.name_last,
                "email": item.email,
                "username": item.username,
                "password": item.password,
                "username": item.username,
                "is_admin": item.is_admin,
                "is_super_admin": item.is_super_admin,
                "is_student": item.is_student,
                "is_instructor": item.is_instructor,
                "progress_score": item.progress_score,
                "gender": item.gender,
                "active": item.active
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
                "name_last": item.name_last,
                "email": item.email,
                "username": item.username,
                "password": item.password,
                "username": item.username,
                "is_admin": item.is_admin,
                "is_super_admin": item.is_super_admin,
                "is_student": item.is_student,
                "is_instructor": item.is_instructor,
                "progress_score": item.progress_score,
                "gender": item.gender,
                "active": item.active
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
                "name_last": item.name_last,
                "email": item.email,
                "username": item.username,
                "password": item.password,
                "username": item.username,
                "is_admin": item.is_admin,
                "is_super_admin": item.is_super_admin,
                "is_student": item.is_student,
                "is_instructor": item.is_instructor,
                "progress_score": item.progress_score,
                "gender": item.gender,
                "active": item.active
            }

            output.append(item_data)


        return jsonify(output)

    # allows one to create a new user
    @APP.route('/user', methods=['POST'])
    def create():

        data = request.get_json()

        u = table()

        u.email = data["email"]
        u.is_admin = data["is_admin"]
        u.is_instructor = data["is_instructor"]
        u.is_student = data["is_student"]
        u.is_super_admin = data["is_super_admin"]
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
            return jsonify({"message": "invalid input - integrity error"}), 400

        except PendingRollbackError:

            SESSION.rollback()

            return jsonify({"message": "invalid input - PendingRollbackError"}), 400

        return jsonify({"message": "user_created"}), 201


    # allows one to delete a user
    # TODO: consider further security policies
    @APP.route('/user/<id>', methods=['DELETE'])
    def delete(id):
        item = SESSION.query(table).filter(table.id == id).first()

        if not item: return jsonify({"Message":"No User by ID"}), 404

        item.active = False

        try:
            SESSION.add(item)
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500

        return jsonify({"message": "user_deleted"})

    # allows one to update user data
    # intended for use in user profiles in edit mode
    # TODO: consider further changes
    @APP.route('/user/<id>', methods=['PUT'])
    def update(id):

        data = request.get_json()

        u = SESSION.query(table).filter(table.id == id).first()

        if not u:
            return jsonify({"message": "User not found"}), 404

        u.email = data["email"]
        u.password = generate_password_hash(data["password"], method='pbkdf2:sha256')
        u.username = data["username"]
        u.name_given= data["name_given"]
        u.name_last = data["name_last"]

        try:
            SESSION.add(u)
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500

        return jsonify({"message":"user updated"}), 200

    # grants or takes away user priveliges to users
    # requires admin level access before proceeding
    @APP.route('/user/<id>/grant', methods=['PUT'])
    def grant_priveliges_user(id):

        data = request.get_json()

        u = SESSION.query(table).filter(table.id == id).first()

        if not u:
            return jsonify({"message": "User not found"}), 404

        u.is_admin = data["is_admin"]
        u.is_instructor = data["is_instructor"]
        u.is_student = data["is_student"]
        u.is_super_admin = data["is_super_admin"]

        try:
            SESSION.add(u)
            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            return jsonify({"message": "Error occurred", "error": str(e)}), 500

        return jsonify({"message":"user privileges updated"}), 200

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

    @APP.route('/user/<id>/study-groups', methods=['GET'])
    def get_user_study_groups_detailed(id):
        u = SESSION.query(table).filter(table.id == id).first()

        if not u:
            return jsonify({"message": "User not found"}), 404

        output = []
        for membership in u.study_groups_membership:
            study_group = membership.study_group
            course = study_group.courses
            group_data = {
                "group_id": study_group.id,
                "group_name": study_group.name,
                "course_name": course.course_name,
                "course_code": course.course_code,
                "is_leader": membership.is_leader,
                "join_date": membership.join_date.isoformat(),
                "max_members": study_group.max_members,
                "course_id": course.id
            }
            output.append(group_data)

        return jsonify(output)

    @APP.route('/user/<id>/teaching-courses', methods=['GET'])
    def get_instructor_courses(id):
        u = SESSION.query(table).filter(table.id == id).first()

        if not u:
            return jsonify({"message": "User not found"}), 404

        if not u.is_instructor:
            return jsonify({"message": "User is not an instructor"}), 403

        output = []
        for course in u.courses_created:
            course_data = {
                "id": course.id,
                "course_code": course.course_code,
                "course_name": course.course_name,
                "description": course.description,
                "is_published": course.is_published,
                "created_at": course.created_at.isoformat(),
                "updated_at": course.updated_at.isoformat(),
                "term_id": course.term_id
            }
            output.append(course_data)

        return jsonify(output)

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
        if auth is None:
            return jsonify({"message": "no user credentials"}), 401

        params = auth.parameters
        username = params.get('username')
        password = params.get('password')

        u, can_login = table.check_login_credentials(SESSION, username, password)

        if can_login:
            # Store username in session
            session['user'] = u.username

            token = jwt.encode({
                'user': u.username,
                'exp': datetime.now() + timedelta(seconds=10),
                'roles': table.get_roles_list(u)}, APP.secret_key)

            return jsonify({
                "token": token, 
                "user_id": u.id,
                "privileges": {
                    "is_admin": u.is_admin,
                    "is_student": u.is_student,
                    "is_instructor": u.is_instructor,
                    "is_super_admin": u.is_super_admin
                }
            }), 200

        return jsonify({"message": "Invalid credentials"}), 401

    @APP.route('/user/logout', methods=['POST'])
    def logout():
        username = session.get('user')
        if username:
            session.pop('user', None)
            if username in _token_store:
                del _token_store[username]
        return jsonify({"message": "Logged out successfully"}), 200

    @APP.route('/token', methods=['GET'])
    async def get_token():
        """Get or refresh Weavy access token"""
        try:
            refresh = request.args.get('refresh') == "true"
            username = session.get('user')

            if not username:
                return jsonify({"message": "No user in session"}), 401

            # Get user from database to validate existence
            user = SESSION.query(table).filter(table.username == username).first()
            if not user:
                return jsonify({"message": "User not found"}), 404

            if not refresh and username in _token_store:
                return jsonify({"access_token": _token_store[username]})

            async with aiohttp.ClientSession() as http_session:
                async with http_session.post(
                    f"{WEAVY_URL}/api/users/{username}/tokens",
                    headers={'Authorization': f'Bearer {API_KEY}'}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        _token_store[username] = data['access_token']
                        return jsonify({"access_token": data['access_token']})
                    return jsonify({"message": f"Weavy error: {response.status}"}), response.status

        except Exception as e:
            return jsonify({"message": f"Error processing token request: {str(e)}"}), 500

    # get top 10 students by progress score
    @APP.route('/user/top-students', methods=['GET'])
    def get_top_students():
        students = SESSION.query(table).filter(table.is_student == True).all()
        # Calculate scores and sort in Python since we need the calculated value
        students_with_scores = [(student, calculate_progress_score(student)) for student in students]
        sorted_students = sorted(students_with_scores, key=lambda x: x[1], reverse=True)[:10]

        output = []
        for student, score in sorted_students:
            item_data = {
                "id": student.id,
                "name_given": student.name_given,
                "name_last": student.name_last,
                "progress_score": score,
                "active": student.active
            }
            output.append(item_data)

        return jsonify(output)

    @APP.route('/user/<id>/courses', methods=['GET'])
    def get_user_courses(id):
        u = SESSION.query(table).filter(table.id == id).first()
        
        if not u:
            return jsonify({"message": "User not found"}), 404

        output = []
        enrollments = u.enrollments

        for enrollment in enrollments:
            course = enrollment.courses
            course_data = {
                "id": course.id,
                "course_code": course.course_code,
                "course_name": course.course_name,
                "description": course.description,
                "instructor_id": course.instructor_id,
                "enroll_date": enrollment.enroll_date
            }
            output.append(course_data)

        return jsonify(output)

    @APP.route('/user/<id>/courses-not-enrolled', methods=['GET'])
    def get_user_not_enrolled_courses(id):
        u = SESSION.query(table).filter(table.id == id).first()

        if not u:
            return jsonify({"message": "User not found"}), 404
        
        enrolled_course_ids = {enrollment.course_id for enrollment in u.enrollments}
        not_enrolled_courses = SESSION.query(table).filter(~table.id.in_(enrolled_course_ids)).all()

        output = []
        for course in not_enrolled_courses:
            course_data = {
                "id": course.id,
                "course_code": course.course_code,
                "course_name": course.course_name,
                "description": course.description,
                "instructor_id": course.instructor_id,
                "term_id": course.term_id,
                "is_published": course.is_published
            }
            output.append(course_data)

        return jsonify(output)

    @APP.route('/user/<id>/all-scores', methods=['GET'])
    def get_user_all_scores(id):
        u = SESSION.query(table).filter(table.id == id).first()

        if not u:
            return jsonify({"message": "User not found"}), 404

        output = {
            "quiz_scores": [],
            "assignment_scores": [],
            "challenge_scores": []
        }

        # Get quiz scores
        for item in u.quiz_scores:
            quiz = item.quiz
            score_data = {
                "title": quiz.quiz_title,
                "score": item.score,
                "submission_date": item.submission_date.isoformat(),
                "quiz_id": quiz.id
            }
            output["quiz_scores"].append(score_data)

        # Get assignment scores
        for item in u.assignment_scores:
            assignment = item.assignment
            score_data = {
                "title": assignment.assignment_title,
                "score": item.score,
                "submission_date": item.submission_date.isoformat(),
                "assignment_id": assignment.id
            }
            output["assignment_scores"].append(score_data)

        # Get challenge scores
        for item in u.challenge_scores:
            challenge = item.challenge
            score_data = {
                "title": challenge.title,
                "score": item.score,
                "submission_date": item.submission_date.isoformat(),
                "challenge_id": challenge.id
            }
            output["challenge_scores"].append(score_data)

        return jsonify(output)

    @APP.route('/user/<id>/assessment-status', methods=['GET'])
    def get_user_assessment_status(id):
        u = SESSION.query(table).filter(table.id == id).first()

        if not u:
            return jsonify({"message": "User not found"}), 404

        # Get all quizzes with course info and user's quiz scores
        all_quizzes = (SESSION.query(Quiz, Course)
                      .join(Course, Course.id == Quiz.content_id)
                      .all())
        user_quiz_scores = {score.quiz_id: score for score in u.quiz_scores}

        # Get all assignments with course info and user's assignment scores
        all_assignments = (SESSION.query(Assignment, Course)
                         .join(Course, Course.id == Assignment.content_id)
                         .all())
        user_assignment_scores = {score.assignment_id: score for score in u.assignment_scores}

        # Get all challenges with course info and user's challenge scores
        all_challenges = (SESSION.query(DailyChallenge, Course)
                        .join(Course, Course.id == DailyChallenge.content_id)
                        .all())
        user_challenge_scores = {score.challenge_id: score for score in u.challenge_scores}

        output = {
            "quizzes": {
                "completed": [],
                "pending": []
            },
            "assignments": {
                "completed": [],
                "pending": []
            },
            "challenges": {
                "completed": [],
                "pending": []
            }
        }

        # Process quizzes
        for quiz, course in all_quizzes:
            quiz_data = {
                "id": quiz.id,
                "title": quiz.quiz_title,
                "course_name": course.course_name,
                "course_code": course.course_code,
                "score": user_quiz_scores[quiz.id].score if quiz.id in user_quiz_scores else None
            }
            if quiz.id in user_quiz_scores:
                output["quizzes"]["completed"].append(quiz_data)
            else:
                output["quizzes"]["pending"].append(quiz_data)

        # Process assignments
        for assignment, course in all_assignments:
            assignment_data = {
                "id": assignment.id,
                "title": assignment.assignment_title,
                "course_name": course.course_name,
                "course_code": course.course_code,
                "score": user_assignment_scores[assignment.id].score if assignment.id in user_assignment_scores else None
            }
            if assignment.id in user_assignment_scores:
                output["assignments"]["completed"].append(assignment_data)
            else:
                output["assignments"]["pending"].append(assignment_data)

        # Process challenges
        for challenge, course in all_challenges:
            challenge_data = {
                "id": challenge.id,
                "title": challenge.title,
                "course_name": course.course_name,
                "course_code": course.course_code,
                "score": user_challenge_scores[challenge.id].score if challenge.id in user_challenge_scores else None
            }
            if challenge.id in user_challenge_scores:
                output["challenges"]["completed"].append(challenge_data)
            else:
                output["challenges"]["pending"].append(challenge_data)

        return jsonify(output)



