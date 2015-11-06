from functools import wraps
import jwt
from jwt import DecodeError, ExpiredSignature
from settings import TOKEN_SECRET
from flask import  request, jsonify
import os
import requests
import json

GOOGLE_SECRET = os.environ.get('GOOGLE_SECRET') or 'Google Client Secret'

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
        if (appname == 'slack') or (appname == 'qrate' and authHeader == 'qrateToken$123') or (appname == 'stig' and authHeader == 'stigToken$123') or (appname == 'slant' and authHeader == 'slantToken$123'):
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

def google():
    access_token_url = 'https://accounts.google.com/o/oauth2/token'
    people_api_url = 'https://www.googleapis.com/plus/v1/people/me/openIdConnect'

    payload = dict(client_id=request.json['clientId'],
                   redirect_uri=request.json['redirectUri'],
                   client_secret=GOOGLE_SECRET,
                   code=request.json['code'],
                   grant_type='authorization_code')

    # Step 1. Exchange authorization code for access token.
    r = requests.post(access_token_url, data=payload)
    token = json.loads(r.text)
    headers = {'Authorization': 'Bearer {0}'.format(token['access_token'])}

    # Step 2. Retrieve information about the current user.
    r = requests.get(people_api_url, headers=headers)
    profile = json.loads(r.text)
    
    print 'token is'+str(profile)

    


                
