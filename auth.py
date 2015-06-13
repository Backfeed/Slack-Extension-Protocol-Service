from datetime import datetime, timedelta
import os
import jwt
import json
import requests
from functools import wraps
from urlparse import parse_qs, parse_qsl
from urllib import urlencode
from flask import  g, request, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash
from jwt import DecodeError, ExpiredSignature
import urllib2
import math

from db import session
import classes as cls


# TBD: move to settings 
SLACK_SECRET = os.environ.get('SLACK_SECRET') or 'e7efc9a81d4043defb7b7e27816ae27e'
TOKEN_SECRET = os.environ.get('SECRET_KEY') or 'JWT Token Secret String'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authHeader = request.headers.get('x-access-token')
        if not authHeader:
            response = jsonify(message='Missing authorization header:'+str(authHeader))
            response.status_code = 401
            return response

        try:
            print "Inside login_required"
            payload = parse_token(request)
        except DecodeError:
            response = jsonify(message='Token is invalid')
            response.status_code = 401
            return response
        except ExpiredSignature:
            response = jsonify(message='Token has expired')
            response.status_code = 401
            return response

        g.user_id = payload['sub']
        g.slackTeamId = payload['slackTeamId']
        g.slackTeamName = payload['slackTeamName']
        print "g.slackTeamId"+str(g.slackTeamId )
        print "g.slackTeamName"+str(g.slackTeamName )
        print "g.user_id"+str(g.user_id )
        return f(*args, **kwargs)

    return decorated_function



# API - ME :
def me():
    print "Inside me"
    print "g.slackTeamId"+str(g.slackTeamId )
    print "g.slackTeamName"+str(g.slackTeamName )
    print "g.user_id"+str(g.user_id )
    if(not g.user_id):
        print 'User Not Logged In.',404
        return 'User Not Logged In.',404
	
    #user = User.query.filter_by(id=g.user_id).first()
    user = session.query(cls.User).filter(cls.User.id == g.user_id).first()
    
    if(not user):
        print 'User Not Logged In.',404
        return 'User Not Logged In.',404	
    
    return jsonify(dict(id=user.slack_id,displayName=user.name,userId=user.id))

def create_token(user,slackTeamId,slackTeamName):
    print "Inside create token"
    payload = {
        'sub': user.id,
        'slackTeamId' : slackTeamId,
        'slackTeamName' : slackTeamName,
        #'iat': datetime.now(),
        'exp': datetime.now() + timedelta(days=14)
    }
    token = jwt.encode(payload, TOKEN_SECRET)
    return token.decode('unicode_escape')


def parse_token(req):
    print "Inside parse token"
    authHeader = req.headers.get('x-access-token')
    print 'parse_token: authHeader:'+str(authHeader)
    token = authHeader.split()[1]
    return jwt.decode(token, TOKEN_SECRET)

def login():
    print "Inside login"
    user = User.query.filter_by(email=request.json['email']).first()
    if not user or not user.check_password(request.json['password']):
        response = jsonify(message='Wrong Email or Password')
        response.status_code = 401
        return response
    token = create_token(user)
    return jsonify(token=token)


def signup():
    print "Inside signup"
    user = User(email=request.json['email'], password=request.json['password'])
    db.session.add(user)
    db.session.commit()
    token = create_token(user)
    return jsonify(token=token)


# Services Auth Routes:
def slack():
    print "Inside slack"
    access_token_url = 'https://slack.com/api/oauth.access'
    users_api_url = 'https://slack.com/api/auth.test'

    params = {
        'client_id': request.json['clientId'],
        'redirect_uri': request.json['redirectUri'],
        'client_secret': SLACK_SECRET,
        'code': request.json['code']
    }

    # Step 1. Exchange authorization code for access token.
    r = requests.get(access_token_url, params=params)
    print 'r.text:'+str(r.text)

    response = json.loads(r.text)
    print str(response)
    access_token = response["access_token"]
    
    headers = {'User-Agent': 'DEAP'}
    print 'access_token:'+str(access_token)

    # Step 2. Retrieve information about the current user.
    r = requests.get(users_api_url, params={'token':access_token}, headers=headers)
    profile = json.loads(r.text)
    print 'slack profile:'+str(profile)
    	   
    # Step 3. (optional) Link accounts.
    if request.headers.get('x-access-token'):
        #user = User.query.filter_by(slack=profile['user_id']).first()
        user = session.query(cls.User).filter(cls.User.slack_id == profile['user_id']).first()

        if user:
            response = jsonify(message='There is already a Slack account that belongs to you')
            response.status_code = 409
            return response

        payload = parse_token(request)

        #user = User.query.filter_by(id=payload['sub']).first()
        user = session.query(cls.User).filter(slc.User.id == payload['sub']).first()

        if not user:
            response = jsonify(message='User not found')
            response.status_code = 400
            return response

        u = User(slack_id=profile['user_id'], name=profile['user'],tokens = 100,reputation = 100)
        session.add(u)
        session.commit()
        token = create_token(u,profile['team_id'],profile['team'])
        return jsonify(token=token)

    # Step 4. Create a new account or return an existing one.
    #user = User.query.filter_by(slack=profile['user_id']).first()
    user = session.query(cls.User).filter(cls.User.slack_id == profile['user_id']).first()

    if user:
        token = create_token(user,profile['team_id'],profile['team'])
        return jsonify(token=token)

    print 'slack profile:'+str(profile)
    #u = cls.User(slack_id=profile['user_id'], name=profile['user'])
    jsonStr = {"slack_id":profile['user_id'],"name":profile['user'],'tokens' : 100,'reputation' : 100}
    u = cls.User(jsonStr,session)
    session.add(u)
    session.commit()
    token = create_token(u,profile['team_id'],profile['team'])
    return jsonify(token=token)
