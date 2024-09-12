import enum

from config import connection_string
from typing import List, Optional 

from datetime import date

from sqlalchemy import create_engine, table, column, Enum, Integer, String, Boolean, DECIMAL, ForeignKey

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

engine = create_engine(connection_string)

BASE = declarative_base()

class Gender(enum.Enum):
    private = 0
    female = 1
    male = 2

class User(BASE):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name_given: Mapped[str] = mapped_column(String(30))
    name_last: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(30), unique=True)
    gender: Mapped[int] = mapped_column(Enum(Gender))
    
    username: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column(String(30))

    is_admin: Mapped[bool]
    is_student: Mapped[bool]
    is_instructor: Mapped[bool]

    # refers to the point allocation for student's overall progress
    # should be left zero for instructors
    progress_score: Mapped[int]

    quiz_scores: Mapped[List["QuizScore"]] = relationship(back_populates="user")

    enrollments: Mapped[List["CourseEnrollment"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    assignment_scores: Mapped[List["AssignmentScore"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    challenge_scores: Mapped[List["DailyChallengeScore"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    
    courses_created: Mapped[List["Course"]] = relationship(back_populates="instructor", cascade="all, delete-orphan")

    study_groups_membership: Mapped[List["StudyGroupMembership"]]= relationship(back_populates="member", cascade="all, delete-orphan")

class Quiz(BASE):

    __tablename__ = "quiz"

    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int]
    quiz_title: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(500))
    time_limit: Mapped[float]
    is_published: Mapped[bool]

class QuizScore(BASE):

    __tablename__ = "quiz_score"

    score: Mapped[int]
    submission_date: Mapped[date]

    # FOREIGN KEY COLUMNS
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quiz.id"), primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

    user: Mapped[List["User"]] = relationship(back_populates="quiz_scores")


# TODO - CURRENTLY INCOMPLETE
class Term(BASE):

    __tablename__ = "term"

    id: Mapped[int] = mapped_column(primary_key=True)



class LessonMaterial(BASE):

    __tablename__ = "lesson_material"

    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("content.id"))
    material_title: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(500))
    material_url: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[date]

    content: Mapped["Content"] = relationship(back_populates="lesson_materials")


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

    is_published: Mapped[bool]
    created_at: Mapped[date]
    updated_at: Mapped[date]

    # foreign key relationships
    
    instructor: Mapped[User] = relationship(back_populates="courses_created")

    content_list: Mapped[List["Content"]] = relationship(back_populates="course")

    enrollments: Mapped[List["CourseEnrollment"]] = relationship(back_populates="course")

    study_groups: Mapped[List["Course"]] = relationship(back_populates="course")


class CourseEnrollment(BASE):

    __tablename__ = "course_enrollment"

    enroll_date: Mapped[date]

    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

    # foreign key relationships
    
    course: Mapped[Course] = relationship(back_populates="enrollments")
    student: Mapped[User] = relationship(back_populates="enrollments")


class Assignment(BASE):

    __tablename__ = "assignment"

    assignment_title: Mapped[str] = mapped_column(String(30))

    id: Mapped[int] = mapped_column(primary_key=True)
    
    content_id: Mapped[int] = mapped_column(ForeignKey("content.id"))
    
    description: Mapped[str] = mapped_column(String(500))
    deadline: Mapped[date]
    max_score: Mapped[float]
    grading_criteria: Mapped[str]  = mapped_column(String(500))
    instructions: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[date]
    
    submission_format: Mapped[str] = mapped_column(String(10))
    updated_at: Mapped[date]

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
    
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))

    type: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[date]

    lesson_materials: Mapped[List["LessonMaterial"]] = relationship(back_populates="content")
    course: Mapped["Course"] = relationship(back_populates="content_list")

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

class StudyGroup(BASE):
    __tablename__ = "study_group"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    course_id: Mapped[int] = mapped_column()
    max_members = Mapped[int]

    course: Mapped["Course"]=relationship(back_populates="study_groups")

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
    engine = create_engine(connection_string)

    with Session(engine) as session:
        BASE.metadata.create_all(engine)


