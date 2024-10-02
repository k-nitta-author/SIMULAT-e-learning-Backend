from functools import wraps
from flask import request, jsonify
import jwt

from setup import APP

def token_required(role):

    def wrapper(func):
        @wraps(func)
        def f(*args,**kwargs):
            try:
                token = request.authorization.token

            except AttributeError:
                return jsonify({"message": "token is missing!"}), 403

            if not token:
                return jsonify({"message": "token is missing!"}), 403
        
            try:
                data = jwt.decode(token, APP.secret_key, algorithms="HS256")

                if not role in data['roles'] or 'admin' in data['roles']: return jsonify({"message": "insufficient role"}), 403

            except:
                return jsonify({"message": "Token is invlalid"}), 403
            
            return func(*args,**kwargs)
            
        return f

    return wrapper
    

