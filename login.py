import flask

from flask import Flask, session, request, jsonify, make_response, render_template
from flask_restful import Api

# the below are for configuring the token
import jwt
from functools import wraps
from datetime import datetime, timedelta

# used for decorating functions, demanding they nhave a valid token
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token: return jsonify({"messsage": "token is missing"}, 401)
        
        try:
            data = jwt.decode(token, 'SECRET')

        except:
            return jsonify({"Alert!": 'Invalid token'})

    
        return func(*args, **kwargs)
    
    return decorated