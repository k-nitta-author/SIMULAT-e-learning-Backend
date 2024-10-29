import enum

from typing import List 

from datetime import date
from os import environ


from sqlalchemy import create_engine, Enum, String, ForeignKey, CheckConstraint

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.exc import ProgrammingError

from werkzeug.security import check_password_hash

engine = create_engine(environ.get("CONNECTION_STRING"))

BASE = declarative_base()


# did not know how to best encode gender into database
# TODO: consider modifying if there is issue 
class Gender(enum.Enum):
    private = 0
    female = 1
    male = 2
    other = 3

class User(BASE):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name_given: Mapped[str] = mapped_column(String(30))
    name_last: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(30), unique=True)
    gender: Mapped[int] = mapped_column(String(30))
    
    # user's login credentials
    # user is meant to login to the login api call to gain token
    # the client would then use token for all tasks that need
    # authentication
    username: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column(String(110))

    # roles for access priveliges
    # a user may have any combination of the below roles
    is_admin: Mapped[bool]
    is_student: Mapped[bool]
    is_instructor: Mapped[bool]
    is_super_admin: Mapped[bool]

    # refers to the point allocation for student's overall progress
    # badges are tentatively allocated based on progress score
    # should be left zero for instructors
    # TODO: consider changing that, make badge earning more interactive, dynamic
    progress_score: Mapped[int]

    active: Mapped[bool]

    # relationships with other tables
    quiz_scores: Mapped[List["QuizScore"]] = relationship(back_populates="user")
    enrollments: Mapped[List["CourseEnrollment"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    assignment_scores: Mapped[List["AssignmentScore"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    challenge_scores: Mapped[List["DailyChallengeScore"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    courses_created: Mapped[List["Course"]] = relationship(back_populates="instructor", cascade="all, delete-orphan")
    study_groups_membership: Mapped[List["StudyGroupMembership"]]= relationship(back_populates="member", cascade="all, delete-orphan")

    # helper method for authentication
    # returns the user object and the result of their password hash
    # otherwise it gives nothing
    def check_login_credentials(session, u_name, p_word):
        
        u: User = session.query(User).filter_by(username = u_name).first()

        if not u is None:

            return u, check_password_hash(u.password, p_word)
        
        return None, False
    
    # helper method for authorization
    # returns a list of the roles a user has
    # list obviously empty if no roles
    def get_roles_list(u) -> List:

        roles = []

        u: User = u
        
        if u.is_admin: roles.append("admin")
        if u.is_student: roles.append("student")
        if u.is_instructor: roles.append("instructor")
        if u.is_super_admin: roles.append("super_admin")

        return roles

# table for quiz
class Quiz(BASE):

    __tablename__ = "quiz"

    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int]
    quiz_title: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(500))
    time_limit: Mapped[float]
    is_published: Mapped[bool]

    # the term during which the quiz released
    term_id: Mapped[int] = mapped_column(ForeignKey("term.id"))

    # gets the term object for more detailed use
    term: Mapped["Term"] = relationship(back_populates="quizzes")

class QuizScore(BASE):

    __tablename__ = "quiz_score"

    score: Mapped[int]
    submission_date: Mapped[date]

    # FOREIGN KEY COLUMNS
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quiz.id"), primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

    user: Mapped[List["User"]] = relationship(back_populates="quiz_scores")


# The Term table
class Term(BASE):

    __tablename__ = "term"

    # the time period from which term starts and ends
    id: Mapped[int] = mapped_column(primary_key=True)
    school_year_start: Mapped[date] = mapped_column(unique=True)
    school_year_end: Mapped[date] = mapped_column(unique=True)

    # relationships with various other tables
    quizzes: Mapped[List["Quiz"]] = relationship(back_populates="term")
    assignments: Mapped[List["Assignment"]] = relationship(back_populates="term")
    courses:  Mapped[List["Course"]] = relationship(back_populates="term")
    content: Mapped[List["Content"]] = relationship(back_populates="term")

# the Lesson Material table
class LessonMaterial(BASE):

    __tablename__ = "lesson_material"

    
    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("content.id"))
    material_title: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(500))
    material_url: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[date]

    content: Mapped["Content"] = relationship(back_populates="lesson_materials")


# the Daily Challenge table
class DailyChallenge(BASE):

    __tablename__ = "daily_challenge"
        
    id: Mapped[int] = mapped_column(primary_key=True)
    
    content_id: Mapped[int] = mapped_column(ForeignKey("content.id"))

    publication_date: Mapped[date] = mapped_column(nullable=True)
    is_published: Mapped[bool]
    created_at: Mapped[date]
    updated_at: Mapped[date]

    challenge_scores: Mapped[List["DailyChallengeScore"]] = relationship(back_populates="challenge", cascade="all, delete-orphan")


class DailyChallengeScore(BASE):

    __tablename__ = "daily_challenge_score"

    score: Mapped[float]
    submission_date: Mapped[date]

    challenge_id: Mapped[int] = mapped_column(ForeignKey("daily_challenge.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

    # foreign key relationships
    student: Mapped["User"] = relationship(back_populates="challenge_scores")
    challenge: Mapped["DailyChallenge"] = relationship(back_populates="challenge_scores")

class Course(BASE):

    __tablename__ = "course"

    id: Mapped[int] = mapped_column(primary_key=True)

    course_code: Mapped[str] = mapped_column(String(30), unique=True)
    course_name: Mapped[str] = mapped_column(String(30), unique=True)
    description: Mapped[str] = mapped_column(String(500))


    instructor_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    term_id: Mapped[int] = mapped_column(ForeignKey("term.id"))

    is_published: Mapped[bool]
    created_at: Mapped[date]
    updated_at: Mapped[date]

    # foreign key relationships
    
    instructor: Mapped[User] = relationship(back_populates="courses_created")

    content_list: Mapped[List["Content"]] = relationship(back_populates="courses")
    enrollments: Mapped[List["CourseEnrollment"]] = relationship(back_populates="courses")
    study_groups: Mapped[List["StudyGroup"]] = relationship(back_populates="courses")

    term:  Mapped["Term"] = relationship(back_populates="courses")


class CourseEnrollment(BASE):

    __tablename__ = "course_enrollment"

    enroll_date: Mapped[date]

    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

    # foreign key relationships
    
    courses: Mapped[Course] = relationship(back_populates="enrollments")
    student: Mapped[User] = relationship(back_populates="enrollments")


class Assignment(BASE):

    __tablename__ = "assignment"

    assignment_title: Mapped[str] = mapped_column(String(30))

    id: Mapped[int] = mapped_column(primary_key=True)
    
    content_id: Mapped[int] = mapped_column(ForeignKey("content.id"))
    term_id: Mapped[int] = mapped_column(ForeignKey("term.id"))
    
    description: Mapped[str] = mapped_column(String(500))
    deadline: Mapped[date]
    max_score: Mapped[float]
    grading_criteria: Mapped[str]  = mapped_column(String(500))
    instructions: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[date]
    
    submission_format: Mapped[str] = mapped_column(String(10))
    updated_at: Mapped[date]

    term: Mapped["Term"] = relationship(back_populates="assignments")

    scores: Mapped[List["AssignmentScore"]] = relationship(back_populates="assignment", cascade="all, delete-orphan")

class AssignmentScore(BASE):

    __tablename__ = "assignment_score"

    score: Mapped[float]
    submission_date: Mapped[date]
    assignment_id: Mapped[int] = mapped_column(ForeignKey("assignment.id"), primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

    student: Mapped[User] = relationship(back_populates="assignment_scores")
    assignment: Mapped[Assignment] = relationship(back_populates="scores")
    

class Content(BASE):

    __tablename__ = "content"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[date]

    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))
    term_id: Mapped[int] = mapped_column(ForeignKey("term.id"))

    lesson_materials: Mapped[List["LessonMaterial"]] = relationship(back_populates="content")
    courses: Mapped["Course"] = relationship(back_populates="content_list")
    term: Mapped[Term] = relationship(back_populates="content")

class BulletinPost(BASE):
    
    __tablename__ = "bulletin_post"

    id: Mapped[int] = mapped_column(primary_key=True)

    name : Mapped[int]
    description: Mapped[str] = mapped_column(String(500))
    publish_date: Mapped[date]
    is_urgent: Mapped[bool]

    author_uid:  Mapped[int] = mapped_column(ForeignKey("user.id"))  

class Badge(BASE):
    __tablename__ = "badge"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(400))
    pts_required: Mapped[int]

    def get_student_badges(session: Session, u: User):

        score = u.progress_score

        badge_list: list = session.query(Badge).filter(Badge.pts_required <= score).all()

        output_list = [
            {"name":badge.name,
             "description": badge.description,
             "pts_required": badge.pts_required} for badge in badge_list
        ]

        return output_list

class StudyGroup(BASE):
    __tablename__ = "study_group"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))
    max_members = Mapped[int]

    courses: Mapped["Course"]=relationship(back_populates="study_groups")

    memberships: Mapped[List["StudyGroupMembership"]]=relationship(back_populates="study_group", cascade="all, delete-orphan")

class StudyGroupMembership(BASE):

    __tablename__ = "study_group_membership"

    student_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    study_group_id: Mapped[int] = mapped_column(ForeignKey("study_group.id"), primary_key=True)
    join_date: Mapped[date]
    is_leader: Mapped[bool]

    study_group: Mapped["StudyGroup"] = relationship(back_populates="memberships")
    member: Mapped["User"] = relationship(back_populates="study_groups_membership")
    

if __name__ == "__main__":
    engine = create_engine(environ.get("CONNECTION_STRING"))

    with Session(engine) as session:

        try:
            User.__table__.create(bind=engine)
            Term.__table__.create(bind=engine)
            Quiz.__table__.create(bind=engine)
            Term.__table__.create(bind=engine)
            LessonMaterial.__table__.create(bind=engine)
            Assignment.__table__.create(bind=engine)
            AssignmentScore.__table__.create(bind=engine)
            DailyChallenge.__table__.create(bind=engine)
            DailyChallengeScore.__table__.create(bind=engine)
            Content.__table__.create(bind=engine)
            BulletinPost.__table__.create(bind=engine)
            Badge.__table__.create(bind=engine)
            StudyGroup.__table__.create(bind=engine)
            StudyGroupMembership.__table__.create(bind=engine)

        # currently checks if there was a duplicate table error
        except ProgrammingError as e:

            print(e._message)
