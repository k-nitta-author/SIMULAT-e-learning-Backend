from flask import jsonify, request
from tables import Course as table, CourseEnrollment
from tables import User
from tables import DailyChallenge, DailyChallengeScore
from tables import Assignment, AssignmentScore
from tables import Quiz, QuizScore
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
                "term_id": item.term_id,
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
                "term_id": item.term_id,
                "content_list": [{"id": c.id, "type": c.type, "title": c.title, "description": c.description, "url": c.url} for c in item.content_list],
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
    
# this route gets courses a user is enrolled in
@APP.route('/user/<user_id>/enrolled-courses', methods=['GET'])
def get_enrolled_courses(user_id):
    user = SESSION.query(User).filter(User.id == user_id).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404

    enrolled_courses = [
        {
            "id": enrollment.courses.id,
            "course_code": enrollment.courses.course_code,
            "course_name": enrollment.courses.course_name,
            "description": enrollment.courses.description,
            "instructor_id": enrollment.courses.instructor_id,
            "term_id": enrollment.courses.term_id,
            "is_published": enrollment.courses.is_published
        }
        for enrollment in user.enrollments
    ]

    return jsonify(enrolled_courses)

# this route gets courses a user is not enrolled in
@APP.route('/user/<user_id>/not-enrolled-courses', methods=['GET'])
def get_not_enrolled_courses(user_id):
    user = SESSION.query(User).filter(User.id == user_id).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404

    enrolled_course_ids = {enrollment.course_id for enrollment in user.enrollments}
    not_enrolled_courses = SESSION.query(table).filter(~table.id.in_(enrolled_course_ids)).all()

    output = [
        {
            "id": course.id,
            "course_code": course.course_code,
            "course_name": course.course_name,
            "description": course.description,
            "instructor_id": course.instructor_id,
            "term_id": course.term_id,
            "is_published": course.is_published
        }
        for course in not_enrolled_courses
    ]

    return jsonify(output)

# this route enrolls a user in a course
@APP.route('/user/<user_id>/enroll/<course_id>', methods=['POST'])
def enroll_in_course(user_id, course_id):
    user = SESSION.query(User).filter(User.id == user_id).first()
    course = SESSION.query(table).filter(table.id == course_id).first()

    if not user or not course:
        return jsonify({"message": "User or Course not found"}), 404

    enrollment = CourseEnrollment(user_id=user_id, course_id=course_id, enroll_date=datetime.now())

    try:
        SESSION.add(enrollment)
        SESSION.commit()
    except IntegrityError:
        SESSION.rollback()
        return jsonify({"message": "User already enrolled in this course"}), 400
    except Exception as e:
        SESSION.rollback()
        return jsonify({"message": "Error occurred", "error": str(e)}), 500

    return jsonify({"message": "user enrolled in course"}), 201



@APP.route('/course/<id>/publish', methods=['POST'])
def publish_course(id):
    course = SESSION.query(table).filter(table.id == id).first()

    if not course:
        return jsonify({"message": "Course not found"}), 404

    if course.is_published:
        return jsonify({"message": "Course is already published"}), 400

    course.is_published = True
    course.updated_at = datetime.now()

    try:
        SESSION.commit()
    except Exception as e:
        SESSION.rollback()
        return jsonify({"message": "Error occurred", "error": str(e)}), 500

    return jsonify({"message": "Course published successfully"}), 200

# this route gets all pending scores for a user in a course
@APP.route('/course/<course_id>/user/<user_id>/pending-scores', methods=['GET'])
def get_pending_scores(course_id, user_id):
    course = SESSION.query(table).filter(table.id == course_id).first()
    if not course:
        return jsonify({"message": "Course not found"}), 404

    # Get all content IDs for this course
    content_ids = [content.id for content in course.content_list]

    output = {
        "pending_assignments": [],
        "pending_quizzes": [],
        "pending_challenges": []
    }

    # Get assignments without scores
    assignments = SESSION.query(Assignment).filter(
        Assignment.content_id.in_(content_ids)
    ).all()
    for assignment in assignments:
        score = SESSION.query(AssignmentScore).filter(
            AssignmentScore.assignment_id == assignment.id,
            AssignmentScore.student_id == user_id
        ).first()
        if score is None:
            output["pending_assignments"].append({
                "id": assignment.id,
                "title": assignment.assignment_title,
                "deadline": assignment.deadline.isoformat() if assignment.deadline else None
            })

    # Get quizzes without scores
    quizzes = SESSION.query(Quiz).filter(
        Quiz.content_id.in_(content_ids)
    ).all()
    for quiz in quizzes:
        score = SESSION.query(QuizScore).filter(
            QuizScore.quiz_id == quiz.id,
            QuizScore.student_id == user_id
        ).first()
        if score is None:
            output["pending_quizzes"].append({
                "id": quiz.id,
                "title": quiz.quiz_title,
            })

    # Get challenges without scores
    challenges = SESSION.query(DailyChallenge).filter(
        DailyChallenge.content_id.in_(content_ids)
    ).all()
    for challenge in challenges:
        score = SESSION.query(DailyChallengeScore).filter(
            DailyChallengeScore.challenge_id == challenge.id,
            DailyChallengeScore.user_id == user_id
        ).first()
        if score is None:
            output["pending_challenges"].append({
                "id": challenge.id,
                "title": challenge.title,
            })

    return jsonify(output)

# this route grades a quiz submission
@APP.route('/course/<course_id>/quiz/<quiz_id>/grade/<user_id>', methods=['POST'])
def grade_quiz(course_id, quiz_id, user_id):
    quiz = SESSION.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        return jsonify({"message": "Quiz not found"}), 404

    data = request.get_json()
    score = QuizScore(
        quiz_id=quiz_id,
        student_id=user_id,
        score=data['score'],
        submission_date=datetime.now()
    )

    try:
        SESSION.add(score)
        SESSION.commit()
    except IntegrityError:
        SESSION.rollback()
        return jsonify({"message": "Score already exists for this quiz"}), 400
    except Exception as e:
        SESSION.rollback()
        return jsonify({"message": "Error occurred", "error": str(e)}), 500

    return jsonify({"message": "Quiz graded successfully"}), 201

# this route grades an assignment submission
@APP.route('/course/<course_id>/assignment/<assignment_id>/grade/<user_id>', methods=['POST'])
def grade_assignment(course_id, assignment_id, user_id):
    assignment = SESSION.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        return jsonify({"message": "Assignment not found"}), 404

    data = request.get_json()
    score = AssignmentScore(
        assignment_id=assignment_id,
        student_id=user_id,
        score=data['score'],
        submission_date=datetime.now()
    )

    try:
        SESSION.add(score)
        SESSION.commit()
    except IntegrityError:
        SESSION.rollback()
        return jsonify({"message": "Score already exists for this assignment"}), 400
    except Exception as e:
        SESSION.rollback()
        return jsonify({"message": "Error occurred", "error": str(e)}), 500

    return jsonify({"message": "Assignment graded successfully"}), 201

# this route grades a challenge submission
@APP.route('/course/<course_id>/challenge/<challenge_id>/grade/<user_id>', methods=['POST'])
def grade_challenge(course_id, challenge_id, user_id):
    challenge = SESSION.query(DailyChallenge).filter(DailyChallenge.id == challenge_id).first()
    if not challenge:
        return jsonify({"message": "Challenge not found"}), 404

    data = request.get_json()
    score = DailyChallengeScore(
        challenge_id=challenge_id,
        user_id=user_id,
        score=data['score'],
        submission_date=datetime.now()
    )

    try:
        SESSION.add(score)
        SESSION.commit()
    except IntegrityError:
        SESSION.rollback()
        return jsonify({"message": "Score already exists for this challenge"}), 400
    except Exception as e:
        SESSION.rollback()
        return jsonify({"message": "Error occurred", "error": str(e)}), 500

    return jsonify({"message": "Challenge graded successfully"}), 201

