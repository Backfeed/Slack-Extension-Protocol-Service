from datetime import datetime, timedelta
import os
import jwt
import json
import requests
from functools import wraps

from flask import  g, request, jsonify
from jwt import DecodeError, ExpiredSignature
from settings import SLACK_SECRET, TOKEN_SECRET
from db import session
import classes as cls


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authHeader = request.headers.get('x-access-token')
        if not authHeader:
            response = jsonify(message='Missing authorization header:' + str(authHeader))
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
        g.slackAccessToken = payload['slackAccessToken'];
        g.slackUserId = payload['slackUserId']
        return f(*args, **kwargs)

    return decorated_function



# API - ME :
def me():       
    if(not g.user_id):
        print 'User Not Logged In.', 404
        return 'User Not Logged In.', 404	
    user = session.query(cls.User).filter(cls.User.id == g.user_id).first()
    if(not user):
        print 'User Not Logged In.', 404
        return 'User Not Logged In.', 404	  
    return jsonify(dict(imgUrl=user.imgUrl, displayName=user.name, user_realname=user.real_name, userId=user.id, slackTeamId=g.slackTeamId, slackTeamName=g.slackTeamName, slackAccessToken=g.slackAccessToken, slackUserId=g.slackUserId))

def create_token(user, slackTeamId, slackTeamName, slackAccessToken, slackUserId):    
    payload = {
        'sub': user.id,
        'slackTeamId' : slackTeamId,
        'slackTeamName' : slackTeamName,
        'slackAccessToken' : slackAccessToken,
        'slackUserId' : slackUserId,
        # 'iat': datetime.now(),
        'exp': datetime.now() + timedelta(days=14)
    }
    token = jwt.encode(payload, TOKEN_SECRET)
    return token.decode('unicode_escape')


def parse_token(req):    
    authHeader = req.headers.get('x-access-token')
    print 'parse_token: authHeader:' + str(authHeader)
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
        'slackAccessToken': request.form['token'],
    }

    slackAccessToken = params["slackAccessToken"]

    headers = {'User-Agent': 'DEAP'}
    print 'slackAccessToken:' + str(slackAccessToken)

    # Step 2. Retrieve information about the current user.
    r = requests.get(users_api_url, params={'token':slackAccessToken}, headers=headers)
    profile = json.loads(r.text)
    print 'slack profile:' + str(profile)   
    # Step 3. (optional) Link accounts.
    if request.headers.get('x-access-token'):        
        # user = User.query.filter_by(slack=profile['user_id']).first()
        user = session.query(cls.User).filter(cls.User.name == profile['user']).first()

        if user:

            response = jsonify(message='There is already a Slack account that belongs to you')
            response.status_code = 409
            return response

        payload = parse_token(request)

        # user = User.query.filter_by(id=payload['sub']).first()
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
                # associate user and org
                jsonStr = {"user_id":user.id,"organization_id": org.id,"org_tokens":0,"org_reputation":0}     
                userOrg = cls.UserOrganization(jsonStr, session)                
                session.add(userOrg)
                session.commit()

        session.add(u)
        session.commit()
        token = create_token(u, profile['team_id'], profile['team'], orgexists)
        return jsonify(token=token)
    
        
    user = session.query(cls.User).filter(cls.User.slackId == profile['user_id']).first()
    orgs = session.query(cls.Organization).filter(cls.Organization.slack_teamid == profile['team_id']).all()
    orgChannelId = ''
    count = 1
    # getting all orgs from current slack team
    for org in orgs:
            # sync the extension db with all the members currently exists in slack team
            syncUsers(org.id, slackAccessToken)
            if count == 1:
                orgChannelId = org.channelId
            else:
                orgChannelId = orgChannelId + ',' + org.channelId
            count = count + 1;
    print 'orgChannelId is' + str(orgChannelId);
    if user:
        token = create_token(user, profile['team_id'], profile['team'], slackAccessToken, profile['user_id'])
        return jsonify(token=token, orgChannelId=orgChannelId)
    
    # getting additional info about user
    userInfo = requests.get('https://slack.com/api/users.info', params={'token':slackAccessToken, 'user':profile['user_id']}, headers=headers)
    userData = json.loads(userInfo.text)['user']
    # create user in DB if this is the first time login into slack extension
    jsonStr = {"slackId":profile['user_id'], "name":profile['user'], "real_name":userData['profile']['real_name'], "imgUrl":userData['profile']['image_48'], "imgUrl72":userData['profile']['image_72']}
    u = cls.User(jsonStr, session)
    session.add(u)
    session.commit()

    token = create_token(u, profile['team_id'], profile['team'], slackAccessToken, profile['user_id'])
    return jsonify(token=token, orgChannelId=orgChannelId)

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
    print 'r.text:' + str(r.text)

    response = json.loads(r.text)
    print str(response)
    slackAccessToken = response["slackAccessToken"]
    
    headers = {'User-Agent': 'DEAP'}
    print 'slackAccessToken:' + str(slackAccessToken)

    # Step 2. Retrieve information about the current user.
    r = requests.get(users_api_url, params={'token':slackAccessToken}, headers=headers)
    profile = json.loads(r.text)
    print 'slack profile:' + str(profile)   
    # Step 3. (optional) Link accounts.
    if request.headers.get('x-access-token'):        
        user = session.query(cls.User).filter(cls.User.name == profile['user']).first()

        if user:
            
            response = jsonify(message='There is already a Slack account that belongs to you')
            response.status_code = 409
            return response

        payload = parse_token(request)

        # user = User.query.filter_by(id=payload['sub']).first()
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
                # associate user and org
                jsonStr = {"user_id":user.id,"organization_id": org.id,"org_tokens":0,"org_reputation":0}     
                userOrg = cls.UserOrganization(jsonStr, session)                
                session.add(userOrg)
                session.commit()
                
        session.add(u)
        session.commit()
        token = create_token(u, profile['team_id'], profile['team'], orgexists)
        return jsonify(token=token)

    user = session.query(cls.User).filter(cls.User.slackId == profile['user_id']).first()
    orgs = session.query(cls.Organization).filter(cls.Organization.slack_teamid == profile['team_id']).all()   
    for org in orgs:
            syncUsers(org.id, slackAccessToken)            
    if user:
        token = create_token(user, profile['team_id'], profile['team'], slackAccessToken, profile['user_id'])
        return jsonify(token=token)

    jsonStr = {"slackId":profile['user_id'], "name":profile['user']}
    u = cls.User(jsonStr, session)
    session.add(u)
    session.commit()
    
    token = create_token(u, profile['team_id'], profile['team'], slackAccessToken, profile['user_id'])
    return jsonify(token=token)


def syncUsers(orgId, slackAccessToken):
    # get all  the db users
    usersInSystem = session.query(cls.User).all()
    usersInSystem.sort(key=lambda x: x.id, reverse=True)
    # get al user organizations in this org
    userOrgs = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == orgId)
    usersOrgDic = {}
    for userOrg in userOrgs:                
        usersOrgDic[userOrg.user_id] = userOrg.id
    # get all slack users
    team_users_api_url = 'https://slack.com/api/users.list'
    headers = {'User-Agent': 'DEAP'}
    r = requests.get(team_users_api_url, params={'token':slackAccessToken}, headers=headers)
    slackUsers = json.loads(r.text)['members']
    usersDic = {}
    usersDic1 = {}
    for user in usersInSystem:                
        usersDic[user.slackId] = user.id
            
        
    for slackUser in slackUsers :
        if slackUser['deleted'] == True :
            continue
        if slackUser['is_bot'] == True :
            continue
        try:
            userId = usersDic[slackUser['id']]
        except KeyError:
            jsonStr = {"slackId":slackUser['id'], "name":slackUser['name'], "imgUrl":slackUser['profile']['image_48'], "imgUrl72":slackUser['profile']['image_72'], "real_name":slackUser['profile']['real_name']}
            u = cls.User(jsonStr, session)
            session.add(u) 
            session.flush() 
            userId = u.id
        
        userOrg = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == orgId).filter(cls.UserOrganization.user_id == userId).first()
            
        # associate user and org if there are not associated earlier
        if not userOrg:
            jsonStr = {"user_id":userId,"organization_id": orgId,"org_tokens":0,"org_reputation":0}     
            userOrg = cls.UserOrganization(jsonStr, session)
            session.add(userOrg)
            session.commit()
                
            
                
