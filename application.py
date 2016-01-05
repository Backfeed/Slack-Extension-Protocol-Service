"""
#!/usr/bin/env python
"""

from flask import Flask,json
# -*- coding: utf-8 -*-
from flask.ext.restful import Api
from flask import send_file
import os

from resources import UserResource, MilestoneBidResource, UserSlackResource
from resources import BidResource
from resources import ContributionResource,PendingContributionResource
from resources import CloseContributionResource
from resources import AllContributionResource
from resources import AllUserResource
from resources import ContributionStatusResource
from resources import OrganizationResource
from resources import OrganizationTokenExistsResource
from resources import OrganizationCodeExistsResource
from resources import getAllSlackUsersResource
from resources import AllOrganizationResource
from resources import BidContributionResource
from resources import MilestoneBidContributionResource
from resources import MemberStatusResource
from resources import ChannelOrganizationExistsResource
from resources import MemberOranizationsResource
from resources import MemberStatusAllOrgsResource
from resources import MilestoneResource
from resources import OrganizationCurrentStatusResource
from resources import AllMilestonesForOrgResource
from resources import AllOrganizationForCurrentTeamResource
from db import session,engine

import auth
import resources
from flask  import request

# Configuration
current_path = os.path.dirname(__file__)
client_path = os.path.abspath(os.path.join(current_path, 'static'))
application = Flask(__name__, static_url_path='', static_folder=client_path)

# Set application.debug=true to enable tracebacks on Beanstalk log output. 
# TBD: Make sure to remove this line before deploying to production.
application.debug=True
application.config['ERROR_404_HELP'] = False

# Set CORS options on app configuration TBD: do we need this ?
""""
from flask.ext.cors import CORS
application.config['CORS_HEADERS'] = "Content-Type"
application.config['CORS_RESOURCES'] = {r"*": {"origins": "*"}}
cors = CORS(application)
"""

# API:
api = Api(application)

api.add_resource(UserResource, '/users/<string:id>/<string:orgId>', endpoint='users')
api.add_resource(UserResource, '/users', endpoint='user')
api.add_resource(UserResource, '/users/<string:id>', endpoint='userUpdate')
api.add_resource(AllUserResource, '/users/all/<string:organizationId>', endpoint='allUser')
api.add_resource(UserSlackResource, '/api/user/<string:slackId>', endpoint='apiusers')

api.add_resource(BidResource, '/bids/<string:id>', endpoint='bids')
api.add_resource(BidResource, '/bids', endpoint='bid')
api.add_resource(BidContributionResource, '/bid/<string:contributionId>/<string:userId>', endpoint='contributionbids')

api.add_resource(ContributionResource, '/contribution', endpoint='contribution')
api.add_resource(PendingContributionResource, '/pendingcontribution', endpoint='pendingcontribution')
api.add_resource(ContributionResource, '/contribution/<string:id>', endpoint='contributions')


api.add_resource(CloseContributionResource, '/contribution/close', endpoint='closeContribution')

api.add_resource(AllContributionResource, '/contribution/all/<string:organizationId>', endpoint='allContribution')
api.add_resource(ContributionStatusResource, '/contribution/status/<string:id>', endpoint='contributionStatus')
api.add_resource(OrganizationTokenExistsResource, '/organization/checkTokenName/<string:tokenName>', endpoint='checkOrgToken')
api.add_resource(OrganizationCodeExistsResource, '/organization/checkCode/<string:code>', endpoint='checkCode')
api.add_resource(MemberOranizationsResource, '/organization/member/<string:slackTeamId>', endpoint='memberOrganizations')
api.add_resource(getAllSlackUsersResource, '/allSlackUsers', endpoint='slackUsers')

api.add_resource(OrganizationResource, '/organization', endpoint='organization')
api.add_resource(OrganizationResource, '/organization/<string:id>', endpoint='organizations')
api.add_resource(ChannelOrganizationExistsResource, '/organization/channel/<string:channelId>/<string:slackTeamId>/<string:userId>', endpoint='channelOrgExists')

api.add_resource(AllOrganizationResource, '/organization/all', endpoint='allOrganizations')
api.add_resource(AllOrganizationForCurrentTeamResource, '/organization/all/team/<string:slackTeamId>', endpoint='allOrganizationsForCurrentTeam')
api.add_resource(MemberStatusResource, '/member/status/<string:userId>/<string:orgId>', endpoint='memberStatus')
api.add_resource(MemberStatusAllOrgsResource, '/member/status/<string:userId>', endpoint='memberStatusAllOrgs')
api.add_resource(OrganizationCurrentStatusResource, '/organization/currentStatus/<string:orgId>/<string:fromMilestone>', endpoint='organizationCurrentStatus')

api.add_resource(MilestoneResource, '/milestone', endpoint='milestone')
api.add_resource(MilestoneResource, '/milestone/<string:id>', endpoint='milestones')
api.add_resource(AllMilestonesForOrgResource, '/milestone/all/<string:id>', endpoint='allMilestonesForOrg')
api.add_resource(MilestoneBidContributionResource, '/milestonebid/<string:milestoneId>/<string:userId>', endpoint='milestonebids')
api.add_resource(MilestoneBidResource, '/milestoneBids', endpoint='milestoneBid')



# Navigation:
@application.route('/')
def index():
    return send_file('static/index.html')
  
# Auth:
@application.route('/api/me',methods=['GET'])
@auth.login_required
def me():
	return auth.me()

@application.route('/auth/ext_login', methods=['POST'])
def ext_login():
	return auth.ext_login()

@application.route('/auth/login', methods=['POST'])
def login():
	return auth.login()

@application.route('/auth/signup', methods=['POST'])
def signup():
	return auth.signup()

@application.route('/auth/slack', methods=['POST'])
def slack():
	return auth.slack()
    
@application.route('/allContributionsFromUser', methods=['POST'])
def allContributionsFromUser():
    return json.dumps(resources.allContributionsFromUser())

@application.route('/allContributionsFromUserV1', methods=['POST'])
def allContributionsFromUserV1():
    return json.dumps(resources.allContributionsFromUserV1())

@application.route('/showreservetokens', methods=['POST'])
def showreservetokens():
    return resources.showreservetokens()

@application.route('/trelloIntegration', methods=['POST'])
def trelloIntegration():
    return resources.trelloIntegration()


@application.route('/allChannelIdsForTeam', methods=['POST'])
def allChannelIdsForTeam():
    return json.dumps(resources.allChannelIdsForTeam())

@application.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()
    
@application.before_request
def db_connect():
    envType = os.getenv('ENV_TYPE', 'Local')
    if envType == 'Local' :
        pass
    if envType == 'Prod' :
        engine.execute("USE ebdb")
    if envType == 'Develop' :
        engine.execute("USE ebdb")        
  
	
if __name__ == '__main__':
      application.run(debug=True,host='0.0.0.0',ssl_context='adhoc')
      #application.run(debug=True)


# BUG: app loads from one session , world eng writes logs on another, app server needs to be restarted for changes from eng to take effect
# TBD: read ENV variable (when in DEV) to aestablish DB engine connect string (DEV/PROD)
# TBD: CORS needed?
# TBD: set up protocols engine as AWS worker tier
