"""
#!/usr/bin/env python
"""

from flask import Flask
from flask.ext.restful import Api
from flask.ext.cors import CORS


application = Flask(__name__)

# Set application.debug=true to enable tracebacks on Beanstalk log output. 
# TBD: Make sure to remove this line before deploying to production.
application.debug=True
 
@application.route('/')
def sanity():
    return "BF Backend is up and running."

# Set CORS options on app configuration

application.config['CORS_HEADERS'] = "Content-Type"
application.config['CORS_RESOURCES'] = {r"*": {"origins": "*"}}
cors = CORS(application)

api = Api(application)

from resources import UserResource
from resources import BidResource
from resources import ContributionResource
from resources import CloseContributionResource

api.add_resource(UserResource, '/users/<string:id>', endpoint='users')
api.add_resource(UserResource, '/users', endpoint='user')

api.add_resource(BidResource, '/bids/<string:id>', endpoint='bids')
api.add_resource(BidResource, '/bids', endpoint='bid')


api.add_resource(ContributionResource, '/contribution', endpoint='contribution')
api.add_resource(ContributionResource, '/contribution/<string:id>', endpoint='contributions')

api.add_resource(CloseContributionResource, '/closeContribution/<string:id>', endpoint='closeContribution')



    
if __name__ == '__main__':
    #application.run(host='0.0.0.0',debug=True)
    application.run(debug=True)


# BUG: app loads from one session , world eng writes logs on another, app server needs to be restarted for changes from eng to take effect
# TBD: read ENV variable (when in DEV) to aestablish DB engine connect string (DEV/PROD)
# TBD: CORS needed?
# TBD: set up  engine as AWS worker tier