"""
#!/usr/bin/env python
"""

from flask import Flask,json
# -*- coding: utf-8 -*-
from flask.ext.restful import Api
from flask import send_file
import os

from resources import AgentResource, AgentFindByHandle, AgentUpdateHandle,\
    AgentFindByNetwork, AgentFindByCollaboration, AgentUpdateNetwork,\
    RegisterAgentResource, GetCollaborationsByNetworkResource,\
    GetCollaborationsByAgentResource, GetContributionByCollaborationResource,\
    GetContributionByAgentResource, GetEvaluationForContributionResource,\
    AllTagsResource, GetLinksByTagResource, GetTagsByLinkResource,\
    GetLinksANDTagsResource
from resources import NetworkResource
from resources import NetworkParameterResource
from resources import CollaborationResource
from resources import ContributionResource
from resources import EvaluationResource
from resources import CollaborationClose
from resources import CollaborationStatsForContributionsResource
from resources import CollaborationStatsForEvaluationsResource
from resources import AgentStatsForContributionsResource
from resources import AgentStatsForEvaluationsResource
from resources import CollaborationParameterResource
from resources import ContributionParameterResource
from resources import EvaluationParameterResource
from resources import AgentParameterResource

from db import session,engine

import auth

# Configuration
current_path = os.path.dirname(__file__)
client_path = os.path.abspath(os.path.join(current_path, 'static'))
application = Flask(__name__, static_url_path='', static_folder=client_path)

# Set application.debug=true to enable tracebacks on Beanstalk log output. 
# TBD: Make sure to remove this line before deploying to production.
application.debug=True
application.config['ERROR_404_HELP'] = False


# API:
api = Api(application)


api.add_resource(AgentResource, '/v1/agents')
api.add_resource(AgentParameterResource, '/v1/agents/<int:id>')
api.add_resource(AgentFindByHandle, '/v1/agents/findByHandle')
api.add_resource(AgentUpdateHandle, '/v1/agents/updateHandle/<int:id>')
api.add_resource(AgentUpdateNetwork, '/v1/agents/updateNetwork/<int:id>')
api.add_resource(AgentFindByNetwork, '/v1/agents/allByNetwork')
api.add_resource(AgentFindByCollaboration, '/v1/agents/allInCollaboration')

api.add_resource(RegisterAgentResource, '/v1/handles/agents/<int:id>')


api.add_resource(NetworkResource, '/v1/networks')
api.add_resource(NetworkParameterResource, '/v1/networks/<int:id>')

api.add_resource(CollaborationResource, '/v1/collaborations')
api.add_resource(CollaborationParameterResource, '/v1/collaborations/<int:id>')
api.add_resource(GetCollaborationsByNetworkResource, '/v1/collaborations/network/<int:id>')
api.add_resource(GetCollaborationsByAgentResource, '/v1/collaborations/agents/<int:id>')

api.add_resource(ContributionResource, '/v1/contributions')
api.add_resource(ContributionParameterResource, '/v1/contributions/<int:id>')
api.add_resource(GetContributionByCollaborationResource, '/v1/contributions/collaborations/<int:id>')
api.add_resource(GetContributionByAgentResource, '/v1/contributions/agent/<int:id>')

api.add_resource(EvaluationResource, '/v1/evaluations/contributions/<int:id>')
api.add_resource(EvaluationParameterResource, '/v1/evaluations/<int:id>')
api.add_resource(GetEvaluationForContributionResource, '/v1/evaluations/contributions/<int:id>')

api.add_resource(CollaborationClose, '/v1/collaborations/close/<int:id>')

api.add_resource(CollaborationStatsForContributionsResource, '/v1/collaborations/status/contributions/<int:id>')
api.add_resource(CollaborationStatsForEvaluationsResource, '/v1/collaborations/status/evaluations/<int:id>')

api.add_resource(AgentStatsForContributionsResource, '/v1/agents/status/contributions/<int:id>')
api.add_resource(AgentStatsForEvaluationsResource, '/v1/agents/status/evaluations/<int:id>')

api.add_resource(AllTagsResource, '/v1/tags')
api.add_resource(GetLinksByTagResource, '/v1/getLinksByTag')
api.add_resource(GetTagsByLinkResource, '/v1/getTagsByLinks')
api.add_resource(GetLinksANDTagsResource, '/v1/search')







# Navigation:
@application.route('/')
def index():
    return send_file('static/index.html')
  
# Auth:
@application.route('/api/me',methods=['GET'])
@auth.login_required
def me():
	return auth.me()
    
@application.route('/auth/google', methods=['POST'])
def google_login():
    return auth.google()

@application.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()
    
@application.before_request
def db_connect():
    envType = os.getenv('ENV_TYPE', 'Local')
    if envType == 'Local' :
        pass
    if envType == 'Staging' :
        engine.execute("USE ebdb")
            
  
	
if __name__ == '__main__':
      #application.run(debug=True,host='0.0.0.0',ssl_context='adhoc')
      application.run(debug=True)


