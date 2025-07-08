import flask

from flask import Flask, request, jsonify, make_response, session
from datetime import datetime, timedelta

# the below are for configuring the token
import jwt
from functools import wraps
from os import environ
from flask_cors import CORS
from setup import APP, SESSION

from resources.user import UserResource
from resources.course import CourseResource
from resources.course_enrollment import CourseEnrollmentResource
from resources.content import ContentResource
from resources.challenge import DailyChallengeResource
from resources.challenge_score import DailyChallengeScoreResource
from resources.quiz import QuizResource
from resources.quiz_score import QuizScoreResource
from resources.lesson_material import LessonMaterialResource
from resources.assignment import AssignmentResource
from resources.assignment_score import AssignmentScoreResource
from resources.badge import BadgeResource
from resources.term import TermResource
from resources.studygroup import StudyGroupResource
from resources.bulletin_post import BulletinResource

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker

from setup import APP
import requests
from flask import send_file
from io import BytesIO

# enable cors
cors = CORS(APP, resources={r"/*": {"origins": "*"}})

APP.config['SECRET KEY'] = environ.get("SECRET_KEY")

# Set session timeout
APP.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Set up the database
database_url = environ.get("CONNECTION_STRING")
if not database_url:
    raise RuntimeError("CONNECTION_STRING environment variable not set")

APP.config['SQLALCHEMY_DATABASE_URI'] = database_url
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_timeout': 30,  # Set the pool timeout to 30 seconds
    'pool_recycle': 1800  # Recycle connections every 30 minutes
}

db = SQLAlchemy(APP)

with APP.app_context():
    engine = db.engine
    Session = sessionmaker(bind=engine)
    SESSION = scoped_session(Session)

@APP.teardown_request
def teardown_request(exception=None):
    # Remove the scoped session
    SESSION.remove()

user_resource = UserResource()
course_resource = CourseResource()
course_enrollment_resource = CourseEnrollmentResource()
content_resource = ContentResource()
challenege_resource = DailyChallengeResource()
challenege_score_resource = DailyChallengeScoreResource()

quiz_resource = QuizResource()
quiz_score_resource = QuizScoreResource()

material_resource = LessonMaterialResource()
assignemnt_res = AssignmentResource()
assignment_score_res = AssignmentScoreResource()

badge_res = BadgeResource()
term_res = TermResource()
study_group = StudyGroupResource()
bulletin_res = BulletinResource()

SUPABASE_URL = environ.get("SUPABASE_URL")
SUPABASE_KEY = environ.get("SUPABASE_KEY")
SUPABASE_BUCKET = environ.get("SUPABASE_BUCKET", "uploads")  # default bucket name

def supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

@APP.route('/files/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    file_data = file.read()
    filename = file.filename
    url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{filename}"
    resp = requests.post(url, headers={**supabase_headers(), "Content-Type": "application/octet-stream"}, data=file_data)
    if resp.status_code in (200, 201):
        return jsonify({'message': 'File uploaded', 'filename': filename}), 201
    return jsonify({'error': 'Upload failed', 'details': resp.text}), 500

@APP.route('/files/<filename>', methods=['GET'])
def download_file(filename):
    url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{filename}"
    resp = requests.get(url, headers=supabase_headers(), stream=True)
    if resp.status_code == 200:
        return send_file(BytesIO(resp.content), download_name=filename, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@APP.route('/files', methods=['GET'])
def list_files():
    url = f"{SUPABASE_URL}/storage/v1/object/list/{SUPABASE_BUCKET}"
    resp = requests.get(url, headers=supabase_headers())
    if resp.status_code == 200:
        files = [item['name'] for item in resp.json()]
        return jsonify({'files': files})
    return jsonify({'error': 'Could not list files', 'details': resp.text}), 500

@APP.route('/files/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{filename}"
    resp = requests.delete(url, headers=supabase_headers())
    if resp.status_code == 200:
        return jsonify({'message': 'File deleted'})
    return jsonify({'error': 'Delete failed', 'details': resp.text}), 500


if __name__ == '__main__':
    APP.run(debug=True, host='0.0.0.0', port=10000)