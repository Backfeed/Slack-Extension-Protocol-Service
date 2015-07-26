from datetime import datetime, timedelta
import os
import jwt
import json
import requests
from functools import wraps
from urlparse import parse_qs, parse_qsl
from urllib import urlencode

from flask import  g, request, redirect,url_for, jsonify
from werkzeug.security import generate_password_hash
from jwt import DecodeError, ExpiredSignature
import urllib2
import math

from db import session
import classes as cls


# TBD: move to settings 
SLACK_SECRET = os.environ.get('SLACK_SECRET') or 'ff21d4660b41b7bee9fef7bb4bf19b79'
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
        g.orgexists=payload['orgexists'] 
        g.orgId=payload['orgId']    
        g.userOrgId=payload['userOrgId']  
        g.access_token = payload['access_token'];
        g.slackUserId = payload['slackUserId']
        return f(*args, **kwargs)

    return decorated_function



# API - ME :
def me():       
    if(not g.user_id):
        print 'User Not Logged In.',404
        return 'User Not Logged In.',404
	
    #user = User.query.filter_by(id=g.user_id).first()
    user = session.query(cls.User).filter(cls.User.id == g.user_id).first()
    userOrgObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == user.id).filter(cls.Organization.id == cls.UserOrganization.organization_id).filter(cls.Organization.slack_teamid == g.slackTeamId).first()
    orgToken = ''
    orgReputation = ''
    existorg = g.orgexists
    userOrganizationId = g.userOrgId
    organizationId = g.orgId
    if(userOrgObj):
        orgToken = userOrgObj.org_tokens;
        orgReputation = userOrgObj.org_reputation
        existorg = "true"
        userOrganizationId = userOrgObj.id
        organizationId = userOrgObj.organization_id
        
        
    
    if(not user):
        print 'User Not Logged In.',404
        return 'User Not Logged In.',404	  
    return jsonify(dict(tokens=orgToken,reputation=orgReputation,displayName=user.name,userId=user.id,slackTeamId=g.slackTeamId,slackTeamName=g.slackTeamName,orgexists=existorg,orgId=organizationId,userOrgId=userOrganizationId,access_token=g.access_token,slackUserId=g.slackUserId))

def create_token(user,slackTeamId,slackTeamName,orgexists,orgId,userOrgId,access_token,slackUserId):    
    payload = {
        'sub': user.id,
        'slackTeamId' : slackTeamId,
        'slackTeamName' : slackTeamName,
        'orgexists' : orgexists,
        'orgId' : orgId,
        'userOrgId' : userOrgId,
        'access_token' : access_token,
        'slackUserId' : slackUserId,
        #'iat': datetime.now(),
        'exp': datetime.now() + timedelta(days=14)
    }
    token = jwt.encode(payload, TOKEN_SECRET)
    return token.decode('unicode_escape')


def parse_token(req):    
    authHeader = req.headers.get('x-access-token')
    print 'parse_token: authHeader:'+str(authHeader)
    token = authHeader.split()[1]
    return jwt.decode(token, TOKEN_SECRET)

def login():
    user = User.query.filter_by(email=request.json['email']).first()
    if not user or not user.check_password(request.json['password']):
        response = jsonify(message='Wrong Email or Password')
        response.status_code = 401
        return response
    token = create_token(user)
    return jsonify(token=token)


def signup():
    user = User(email=request.json['email'], password=request.json['password'])
    db.session.add(user)
    db.session.commit()
    token = create_token(user)
    return jsonify(token=token)


# Services Auth Routes:
def ext_login():
    users_api_url = 'https://slack.com/api/auth.test'

    params = {
        'access_token': request.form['token'],
    }

    access_token = params["access_token"]

    headers = {'User-Agent': 'DEAP'}
    print 'access_token:'+str(access_token)

    # Step 2. Retrieve information about the current user.
    r = requests.get(users_api_url, params={'token':access_token}, headers=headers)
    profile = json.loads(r.text)
    print 'slack profile:'+str(profile)   
    # Step 3. (optional) Link accounts.
    if request.headers.get('x-access-token'):        
        #user = User.query.filter_by(slack=profile['user_id']).first()
        user = session.query(cls.User).filter(cls.User.name == profile['user']).first()

        if user:

            response = jsonify(message='There is already a Slack account that belongs to you')
            response.status_code = 409
            return response

        payload = parse_token(request)

        #user = User.query.filter_by(id=payload['sub']).first()
        user = session.query(cls.User).filter(cls.User.id == payload['sub']).first()

        if not user:
            response = jsonify(message='User not found')
            response.status_code = 400
            return response

        u = User(name=profile['user'])
        org = session.query(cls.Organization).filter(cls.Organization.slack_teamid == profile['team_id']).first()
        orgexists = "true"
        if not org:
            orgexists = "false"
        else:
            userOrg = session.query(cls.UserOrganization).filter(cls.UserOrganization.org_id == org.id).filter(cls.UserOrganization.user_id == user.id).first()
            if not userOrg:
                #associate user and org
                jsonStr = {"user_id":user.id,
                    "organization_id": org.id,
                    "org_tokens":100,
                    "org_reputation":100
                    }     
                userOrg = cls.UserOrganization(jsonStr,session)                
                session.add(userOrg)
                session.commit()

        session.add(u)
        session.commit()
        token = create_token(u,profile['team_id'],profile['team'],orgexists)
        return jsonify(token=token)

    # Step 4. Create a new account or return an existing one.
    #user = User.query.filter_by(slack=profile['user_id']).first()

    org = session.query(cls.Organization).filter(cls.Organization.slack_teamid == profile['team_id']).first()
    orgexists = "true"
    if not org:
        orgexists = "false"
    if org:
        syncUsers(org.id,access_token)
    user = session.query(cls.User).filter(cls.User.name == profile['user']).first()
    if user:

        if org:            
            userOrg = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == org.id).filter(cls.UserOrganization.user_id == user.id).first()
            if not userOrg:
                #associate user and org
                jsonStr = {"user_id":user.id,
                    "organization_id": org.id,
                    "org_tokens":0,
                    "org_reputation":0
                    }     
                userOrg = cls.UserOrganization(jsonStr,session)
                session.add(userOrg)
                session.commit()           
            token = create_token(user,profile['team_id'],profile['team'],orgexists,org.id,userOrg.id,access_token,profile['user_id'])
            return jsonify(token=token)
        token = create_token(user,profile['team_id'],profile['team'],orgexists,'','',access_token,profile['user_id'])
        return jsonify(token=token)

    print 'slack profile:'+str(profile)
    #u = cls.User(slack_id=profile['user_id'], name=profile['user'])
    jsonStr = {"name":profile['user']}
    u = cls.User(jsonStr,session)
    session.add(u)
    session.commit()
    if org:
        userOrg = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == org.id).filter(cls.UserOrganization.user_id == u.id).first()
        if not userOrg:
            #associate user and org
            userOrg = cls.UserOrganization()
            userOrg.org_id = org.id
            userOrg.user_id = u.id
            userOrg.org_tokens = 0
            userOrg.org_reputation = 0;
            session.add(userOrg)
            session.commit()        
        token = create_token(user,profile['team_id'],profile['team'],orgexists,org.id,userOrg.id,access_token,profile['user_id'])
        return jsonify(token=token)

    token = create_token(u,profile['team_id'],profile['team'],orgexists,'','',access_token,profile['user_id'])
    return jsonify(token=token)

# Services Auth Routes:
def slack():
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
        user = session.query(cls.User).filter(cls.User.name == profile['user']).first()

        if user:
            
            response = jsonify(message='There is already a Slack account that belongs to you')
            response.status_code = 409
            return response

        payload = parse_token(request)

        #user = User.query.filter_by(id=payload['sub']).first()
        user = session.query(cls.User).filter(cls.User.id == payload['sub']).first()

        if not user:
            response = jsonify(message='User not found')
            response.status_code = 400
            return response

        u = User(name=profile['user'])
        org = session.query(cls.Organization).filter(cls.Organization.slack_teamid == profile['team_id']).first()
        orgexists = "true"
        if not org:
            orgexists = "false"
        else:
            userOrg = session.query(cls.UserOrganization).filter(cls.UserOrganization.org_id == org.id).filter(cls.UserOrganization.user_id == user.id).first()
            if not userOrg:
                #associate user and org
                jsonStr = {"user_id":user.id,
                    "organization_id": org.id,
                    "org_tokens":100,
                    "org_reputation":100
                    }     
                userOrg = cls.UserOrganization(jsonStr,session)                
                session.add(userOrg)
                session.commit()
                
        session.add(u)
        session.commit()
        token = create_token(u,profile['team_id'],profile['team'],orgexists)
        return jsonify(token=token)

    # Step 4. Create a new account or return an existing one.
    #user = User.query.filter_by(slack=profile['user_id']).first()
    
    org = session.query(cls.Organization).filter(cls.Organization.slack_teamid == profile['team_id']).first()
    orgexists = "true"
    if not org:
        orgexists = "false"
    if org:
        syncUsers(org.id,access_token)
    user = session.query(cls.User).filter(cls.User.name == profile['user']).first()
    if user:
        
        if org:            
            userOrg = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == org.id).filter(cls.UserOrganization.user_id == user.id).first()
            if not userOrg:
                #associate user and org
                jsonStr = {"user_id":user.id,
                    "organization_id": org.id,
                    "org_tokens":0,
                    "org_reputation":0
                    }     
                userOrg = cls.UserOrganization(jsonStr,session)
                session.add(userOrg)
                session.commit()           
            token = create_token(user,profile['team_id'],profile['team'],orgexists,org.id,userOrg.id,access_token,profile['user_id'])
            return jsonify(token=token)
        token = create_token(user,profile['team_id'],profile['team'],orgexists,'','',access_token,profile['user_id'])
        return jsonify(token=token)

    print 'slack profile:'+str(profile)
    #u = cls.User(slack_id=profile['user_id'], name=profile['user'])
    jsonStr = {"name":profile['user']}
    u = cls.User(jsonStr,session)
    session.add(u)
    session.commit()
    if org:
        userOrg = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == org.id).filter(cls.UserOrganization.user_id == u.id).first()
        if not userOrg:
            #associate user and org
            userOrg = cls.UserOrganization()
            userOrg.org_id = org.id
            userOrg.user_id = u.id
            userOrg.org_tokens = 0
            userOrg.org_reputation = 0;
            session.add(userOrg)
            session.commit()        
        token = create_token(user,profile['team_id'],profile['team'],orgexists,org.id,userOrg.id,access_token,profile['user_id'])
        return jsonify(token=token)
    
    token = create_token(u,profile['team_id'],profile['team'],orgexists,'','',access_token,profile['user_id'])
    return jsonify(token=token)

def syncUsers(orgId,access_token):
    # get all  the db users
    usersInSystem= session.query(cls.User).all()
    # get al user organizations in this org
    userOrgs = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == orgId)
    usersOrgDic = {}
    for userOrg in userOrgs:                
        usersOrgDic[userOrg.user_id] = userOrg.id
    # get all slack users
    team_users_api_url = 'https://slack.com/api/users.list'
    headers = {'User-Agent': 'DEAP'}
    r = requests.get(team_users_api_url, params={'token':access_token}, headers=headers)
    slackUsers = json.loads(r.text)['members']
    usersDic = {}
    for user in usersInSystem:                
        usersDic[user.name] = user.id
    for slackUser in slackUsers :
        if slackUser['deleted'] == True :
            continue
        if slackUser['is_bot'] == True :
            continue
        try:
            userId = usersDic[slackUser['name']]
        except KeyError:
            jsonStr = {"name":slackUser['name'],"url":slackUser['profile']['image_24'],"real_name":slackUser['profile']['real_name']}
            u = cls.User(jsonStr,session)
            session.add(u) 
            session.flush() 
            userId = u.id
        
        userOrg = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == orgId).filter(cls.UserOrganization.user_id == userId).first()
        if not userOrg:
            #associate user and org
            jsonStr = {"user_id":userId,
                "organization_id": orgId,
                "org_tokens":0,
                "org_reputation":0
                }     
            userOrg = cls.UserOrganization(jsonStr,session)
            session.add(userOrg)
            session.commit()
                