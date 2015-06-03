"""
#!/usr/bin/env python
"""
from datetime import datetime, timedelta
import os
import jwt
import json
import requests
from functools import wraps
from urlparse import parse_qs, parse_qsl
from urllib import urlencode
from flask import  g, send_file, request, redirect, url_for, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from requests_oauthlib import OAuth1
from jwt import DecodeError, ExpiredSignature
from trello import TrelloApi
import urllib2
import math


from flask import Flask
from flask.ext.restful import Api
from flask.ext.cors import CORS
from flask import send_file
import os

# Configuration
current_path = os.path.dirname(__file__)
client_path = os.path.abspath(os.path.join(current_path, 'static'))

application = Flask(__name__, static_url_path='', static_folder=client_path)

# Set application.debug=true to enable tracebacks on Beanstalk log output. 
# TBD: Make sure to remove this line before deploying to production.
application.debug=True

""" 
@application.route('/')
def sanity():
    return "BF Backend is up and running."
"""

# Set CORS options on app configuration

application.config['CORS_HEADERS'] = "Content-Type"
application.config['CORS_RESOURCES'] = {r"*": {"origins": "*"}}
cors = CORS(application)

api = Api(application)

from resources import UserResource
from resources import BidResource
from resources import ContributionResource
from resources import CloseContributionResource
from resources import AllContributionResource

api.add_resource(UserResource, '/users/<string:id>', endpoint='users')
api.add_resource(UserResource, '/users', endpoint='user')

api.add_resource(BidResource, '/bids/<string:id>', endpoint='bids')
api.add_resource(BidResource, '/bids', endpoint='bid')


api.add_resource(ContributionResource, '/contribution', endpoint='contribution')
api.add_resource(ContributionResource, '/contribution/<string:id>', endpoint='contributions')

api.add_resource(CloseContributionResource, '/contribution/close/<string:id>', endpoint='closeContribution')

api.add_resource(AllContributionResource, '/contribution/all', endpoint='allContribution')



# Navigation Routes:
@application.route('/')
def index():
    return send_file('static/index.html')
    
if __name__ == '__main__':
    #application.run(host='0.0.0.0',debug=True)
    application.run(debug=True)


# BUG: app loads from one session , world eng writes logs on another, app server needs to be restarted for changes from eng to take effect
# TBD: read ENV variable (when in DEV) to aestablish DB engine connect string (DEV/PROD)
# TBD: CORS needed?
# TBD: set up  engine as AWS worker tier