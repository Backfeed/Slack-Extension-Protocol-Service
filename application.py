"""
#!/usr/bin/env python
"""

from flask import Flask
from flask.ext.restful import Api
from flask import send_file
import os

from resources import UserResource
from resources import BidResource
from resources import ContributionResource
from resources import CloseContributionResource
from resources import AllContributionResource
from resources import AllUserResource
from resources import ContributionStatusResource
from resources import OrganizationResource
from resources import ContributionTokenExistsResource
from resources import getAllSlackUsersResource
from resources import AllOrganizationResource
from db import session,engine

import auth

# Configuration
current_path = os.path.dirname(__file__)
client_path = os.path.abspath(os.path.join(current_path, 'static'))
application = Flask(__name__, static_url_path='', static_folder=client_path)

# Set application.debug=true to enable tracebacks on Beanstalk log output. 
# TBD: Make sure to remove this line before deploying to production.
application.debug=True

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
api.add_resource(AllUserResource, '/users/all/<string:organizationId>', endpoint='allUser')

api.add_resource(BidResource, '/bids/<string:id>', endpoint='bids')
api.add_resource(BidResource, '/bids', endpoint='bid')

api.add_resource(ContributionResource, '/contribution', endpoint='contribution')
api.add_resource(ContributionResource, '/contribution/<string:id>', endpoint='contributions')


api.add_resource(CloseContributionResource, '/contribution/close', endpoint='closeContribution')

api.add_resource(AllContributionResource, '/contribution/all/<string:organizationId>', endpoint='allContribution')
api.add_resource(ContributionStatusResource, '/contribution/status/<string:id>/<string:userId>', endpoint='contributionStatus')
api.add_resource(ContributionTokenExistsResource, '/organization/checkTokenName/<string:tokenName>', endpoint='checkOrgToken')
api.add_resource(getAllSlackUsersResource, '/allSlackUsers', endpoint='slackUsers')

api.add_resource(OrganizationResource, '/organization', endpoint='organization')

api.add_resource(AllOrganizationResource, '/organization/all', endpoint='allOrganizations')


# Navigation:
@application.route('/')
def index():
    return send_file('static/index.html')
  
# Auth:
@application.route('/api/me',methods=['GET'])
@auth.login_required
def me():
	return auth.me()

@application.route('/auth/login', methods=['POST'])
def login():
	return auth.login()

@application.route('/auth/signup', methods=['POST'])
def signup():
	return auth.signup()

@application.route('/auth/slack', methods=['POST'])
def slack():
	return auth.slack()

@application.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()
    
    
@application.before_request
def db_connect():
	envType = os.getenv('ENV_TYPE', 'Local')
    print 'envType is'+envType
    if(envType == 'Local'):
        pass
    if(envType == 'Prod'):
        engine.execute("USE ebdb")
    if(envType == 'Stage'):
        engine.execute("USE ebdb")   
	
if __name__ == '__main__':
      application.run(host='0.0.0.0',debug=True)
      #application.run(debug=True)


# BUG: app loads from one session , world eng writes logs on another, app server needs to be restarted for changes from eng to take effect
# TBD: read ENV variable (when in DEV) to aestablish DB engine connect string (DEV/PROD)
# TBD: CORS needed?
# TBD: set up protocols engine as AWS worker tier
