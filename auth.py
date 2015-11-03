from functools import wraps
import jwt
from jwt import DecodeError, ExpiredSignature
from settings import TOKEN_SECRET
from flask import  request, jsonify


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authHeader = request.headers.get('x-access-token')
        appname = request.headers.get('appname')
        if not authHeader or not appname:
            response = jsonify(message='Missing authorization header:' + str(authHeader))
            response.status_code = 401
            return response

        print "Inside login_required"
        if (appname == 'slack') or (appname == 'bookmark' and authHeader == 'bookmarkToken$123') or (appname == 'stig' and authHeader == 'stigToken$123') or (appname == 'slant' and authHeader == 'slantToken$123'):
            if appname == 'slack' :
                try:
                    payload = parse_token(request)
                except DecodeError:
                    response = jsonify(message='Token is invalid')
                    response.status_code = 401
                    return response
                except ExpiredSignature:
                    response = jsonify(message='Token has expired')
                    response.status_code = 401
                    return response
            return f(*args, **kwargs)
        else:
            response = jsonify(message='Header is invalid')
            response.status_code = 401
            return response        

    return decorated_function

def parse_token(authHeader):    
    print 'parse_token: authHeader:' + str(authHeader)
    token = authHeader.split()[1]
    return jwt.decode(token, TOKEN_SECRET)

# API - ME :
def me():       
    return jsonify(dict(message="logged in"))


                
