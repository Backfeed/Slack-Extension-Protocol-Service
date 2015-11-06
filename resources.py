from db import session
# -*- coding: utf-8 -*-
import classes as cls

from flask.ext.restful import reqparse
from flask.ext.restful import abort
from flask.ext.restful import fields
from flask.ext.restful import marshal_with
import json
from auth import login_required
import requests
from flask import g,request

from value_distributer import ValueDistributer 
from datetime import datetime

#from flask.ext.restful import Resource
#Add Authentication required to all resources:
from flask.ext.restful import Resource as FlaskResource
class Resource(FlaskResource):
   method_decorators = [login_required]   # applies to all inherited resources




handle_fields = {
    'id': fields.Integer,
    'handleName': fields.String,
    'handleType': fields.String,
}

agent_handle_fields = {
    'id': fields.Integer,
    'handleName': fields.String,
    'handleType': fields.String,
    'name': fields.String,
    'fullName': fields.String,
    'imgUrl': fields.String,
}

agent_network_fields = {
    'id': fields.Integer,
}



collaboration_fields = {
    'id': fields.Integer,
    'name': fields.String, 
    'tokenName': fields.String,
    'tokenSymbol': fields.String,
    'status': fields.String,
    'similarEvaluationRate': fields.Integer,
    'passingResponsibilityRate': fields.Integer,        
}

agent_collaboration_fields = {
    'id': fields.Integer,
    'name': fields.String, 
    'tokens': fields.Float,  
    'reputation': fields.Float, 
     'imgUrl' : fields.String,
     'fullName':fields.String,
}


evaluation_fields = {
    'id': fields.Integer,
    'contributionId': fields.Integer,
    'agentHandleId': fields.Integer,
    'tokens': fields.Float,
    'stake': fields.Float,
    'reputation': fields.Float,
    'contributionValueAfterEvaluation': fields.Float,
    'timeCreated': fields.DateTime
}

evaluation_nested_fields = {}
evaluation_nested_fields['stake'] = fields.Float
evaluation_nested_fields['tokens'] = fields.Float
evaluation_nested_fields['reputation'] = fields.Float
evaluation_nested_fields['agentId'] = fields.Integer

contributor_nested_fields = {}
contributor_nested_fields['id'] = fields.String
contributor_nested_fields['percentage'] = fields.String
contributor_nested_fields['name'] = fields.String

contribution_fields = {}
contribution_fields['id'] = fields.Integer
contribution_fields['timeCreated'] = fields.DateTime
contribution_fields['agentCollaborationId'] = fields.Integer
contribution_fields['status'] = fields.String
contribution_fields['tokenSymbol'] = fields.String
contribution_fields['tokenName'] = fields.String
contribution_fields['currentValuation'] = fields.Integer
contribution_fields['evaluations'] = fields.Nested(evaluation_nested_fields)
contribution_fields['contributors'] = fields.Nested(contributor_nested_fields)

tag_fields = {}
tag_fields['name'] = fields.String

link_fields = {}
link_fields['name'] = fields.String

    
class AgentResource(FlaskResource):
    @marshal_with(agent_handle_fields)
    def get(self):
        networkId = request.args.get('networkId')
        agents = []
        if(networkId != None ) :
            agentNetworks = session.query(cls.AgentNetwork).filter(cls.AgentNetwork.networkId == networkId).all() 
            
            for agentNetwork in agentNetworks :
                jsonStr = {
                    "id":agentNetwork.agent.id,
                    "name":agentNetwork.agent.name,
                    "imgUrl":agentNetwork.agent.imgUrl
                    }
                agents.append(jsonStr)
        else :
            agentHandles = session.query(cls.AgentHandle).all() 
            for agentHandle in agentHandles :
                agentHandle = fillAgentDetails(agentHandle)
            return agentHandles
    
    
    def delete(self):
        
        agentHandles = session.query(cls.AgentHandle).all()
        for agentHandle in agentHandles :
            deleteAgentHandle(agentHandle)
            
        session.commit()
        
        return "Agents deleted successfully", 200
    

    def post(self):
        name = request.args.get('name')
        if(name == '' or name == None ):
            abort(404, message="name is required")
        jsonStr = {"name":name}
        agent = cls.Agent(jsonStr,session)
        session.add(agent)
        session.flush()
        postData = request.data
        handles = None
        if postData != '' and postData != None :
            postDataJSON = json.loads(postData)
            try :
                handles = postDataJSON['handles']
            except KeyError :
                handles = None
        if handles != None :
            for handle in handles :
                handleName = handle['name']
                handleType = handle['type']
                agentHandle = getAgentByHandleNameAndType(handleName, handleType)
                if agentHandle :
                    abort(404, message="handleName {} and handleType {} already exist".format(handleName,handleType))
                agentHandle = cls.AgentHandle()
                agentHandle.agentId = agent.id
                agentHandle.handleType = handleType
                agentHandle.handleName = handleName
                session.add(agentHandle)
                
        session.commit()
        return {"id":agent.id}, 201
            
class AgentParameterResource(Resource):
    def get(self, id):
        agent = getAgent(id)
        fields = request.args.get('fields')
        if not agent:
            abort(404, message="Agent {} doesn't exist".format(id)) 
        return agentString(agent,fields) 
    
    
    def delete(self, id):
        handleName = request.args.get('handleName')
        handleType = request.args.get('handleType')
        networkId = request.args.get('networkId')
        if(handleName != None and handleType != None):
            agentHandle = getAgentHandle(id)
            if not agentHandle:
                abort(404, message="Agent {} doesn't exist".format(id))
            existingAgentHandle = getAgentByNameAndType(agentHandle.agent.name,handleName, handleType)
            if not existingAgentHandle :
                abort(404, message="agentHandle with {} and handleName: {} and handleType: {} doesn't exist".format(agentHandle.agent.name,handleName,handleType))
            deleteAgentHandle(existingAgentHandle)
            session.commit()
            return "Agent Handle deleted successfully", 200
        elif(networkId != None ) :
            agentNetwork = session.query(cls.AgentNetwork).filter(cls.AgentNetwork.networkId == networkId).filter(cls.AgentNetwork.agentHandleId == id).first() 
            if agentNetwork :
                session.delete(agentNetwork)
            session.commit()
            return "Agent Networks deleted successfully", 200
        else :
            agentHandle = getAgentHandle(id)
            if not agentHandle:
                abort(404, message="Agent {} doesn't exist".format(id))
            deleteAgentHandle(agentHandle)
            session.commit()
            return "Agent deleted successfully", 200
        
        
        
    
    def post(self,id):
        handleName = request.args.get('handleName')
        handleType = request.args.get('handleType')
        if(handleName == '' or handleName == None ):
            abort(404, message="handleName is required")
            
        if(handleType == '' or handleType == None ):
            abort(404, message="handleType is required")
            
        agentHandle = getAgentHandle(id)
        
        if not agentHandle :
            abort(404, message="Agent {} does not  exist".format(id))
        existingAgentHandle = getAgentByIdAndType(agentHandle.agent.id,handleName,handleType)
        if existingAgentHandle :
            abort(404, message="Agent {} with handleName {} and handleType {} already exist".format(id,handleName,handleType))
        
        
        agentHandle = cls.AgentHandle()
        agentHandle.agentId = agentHandle.agent.id
        agentHandle.handleType = handleType
        agentHandle.handleName = handleName
        session.add(agentHandle)
        session.commit()   
        return agentHandle, 201
    
class RegisterAgentResource(FlaskResource):

    def post(self,id):
        agent = getAgent(id)
        if not agent:
            abort(404, message="Agent {} doesn't exist".format(id))
        postData = request.data
        handles = None
        if postData != '' and postData != None :
            postDataJSON = json.loads(postData)
            try :
                handles = postDataJSON['handles']
            except KeyError :
                handles = None
        if handles != None :
            for handle in handles :
                handleName = handle['name']
                handleType = handle['type']
                agentHandle = getAgentByHandleNameAndType(handleName, handleType)
                if agentHandle :
                    abort(404, message="handleName {} and handleType {} already exist".format(handleName,handleType))
                agentHandle = cls.AgentHandle()
                agentHandle.agentId = agent.id
                agentHandle.handleType = handleType
                agentHandle.handleName = handleName
                session.add(agentHandle)
                
        session.commit()
        return {"id":agent.id}, 201
    
    def delete(self,id):
        agent = getAgent(id)
        if not agent:
            abort(404, message="Agent {} doesn't exist".format(id))
        postData = request.data
        handles = None
        if postData != '' and postData != None :
            postDataJSON = json.loads(postData)
            try :
                handles = postDataJSON['handles']
            except KeyError :
                handles = None
        if handles != None :
            for handle in handles :
                handleName = handle['name']
                handleType = handle['type']
                agentHandle = getAgentByHandleNameAndType(handleName, handleType)
                if not agentHandle :
                    abort(404, message="handleName {} and handleType {} doesn't exist".format(handleName,handleType))
                session.delete(agentHandle)
                
        session.commit()
        return "agent handles deleted successfully", 200
    
class AgentFindByHandle(Resource):
    @marshal_with(agent_handle_fields)
    def get(self):
        handleName = request.args.get('handleName')
        handleType = request.args.get('handleType')
        if(handleName == '' or handleName == None ):
            abort(404, message="handleName is required")
            
        if(handleType == '' or handleType == None ):
            abort(404, message="handleType is required")
            
        agentHandles = session.query(cls.AgentHandle).filter(cls.AgentHandle.handleName == handleName).filter(cls.AgentHandle.handleType == handleType).all()
        for agentHandle in agentHandles:
            agentHandle = fillAgentDetails(agentHandle)
        return agentHandles
    
class AgentFindByNetwork(Resource):
    @marshal_with(agent_handle_fields)
    def get(self):
        networkId = request.args.get('networkId')
        if(networkId != None ) :
            network = session.query(cls.Network).filter(cls.Network.id == networkId).first()
            if not network :
                abort(404, message="Network {} does not exists".format(networkId))
            agentNetworks = network.agentNetworks
            agentHandlesList = []
            for agentNetwork in agentNetworks:
                agentHandle = agentNetwork.agentHandle
                agentHandle = fillAgentDetails(agentHandle)
                agentHandlesList.append(agentHandle)
        return agentHandlesList
    
class AgentFindByCollaboration(Resource):
    @marshal_with(agent_handle_fields)
    def get(self):
        collaborationId = request.args.get('collaborationId')
        if(collaborationId != None ) :
            collaboration = session.query(cls.Collaboration).filter(cls.Collaboration.id == collaborationId).first()
            if not collaboration :
                abort(404, message="Collaboration {} does not exists".format(collaborationId))
            agentCollaborations = collaboration.agentCollaborations
            agentHandlesList = []
            for agentCollaboration in agentCollaborations:
                agentHandle = agentCollaboration.agentHandle
                agentHandle = fillAgentDetails(agentHandle)
                agentHandlesList.append(agentHandle)
        return agentHandlesList
    
class AgentUpdateHandle(Resource):
    @marshal_with(agent_handle_fields)
    def put(self,id):
        handleName = request.args.get('handleName')
        handleType = request.args.get('handleType')
        if(handleName == '' or handleName == None ):
            abort(404, message="handleName is required")
            
        if(handleType == '' or handleType == None ):
            abort(404, message="handleType is required")
            
        agentHandle = getAgentHandle(id)
        if not agentHandle :
            abort(404, message="Agent {} does not exist".format(id))
        existingAgentHandle = getAgentByNameAndType(agentHandle.agent.name, handleName, handleType)
        if existingAgentHandle :
            abort(404, message="Agent {} with handleName {} and handleType {} already exist".format(agentHandle.agent.name,handleName,handleType))
        agentHandle = cls.AgentHandle()
        agentHandle.handleName = handleName
        agentHandle.handleType = handleType
        agentHandle.agentId = id
        session.add(agentHandle)
        session.commit()
        return agentHandle
    
class AgentUpdateNetwork(Resource):
    @marshal_with(agent_network_fields)
    def put(self,id):
        networkId = request.args.get('networkId')
        if(networkId == '' or networkId == None ):
            abort(404, message="networkId is required")
        network = session.query(cls.Network).filter(cls.Network.id == networkId).first()
        if not network :
            abort(404, message="Network {} does not exists".format(networkId))
        agentHandle = getAgentHandle(id)
        if not agentHandle :
            abort(404, message="agentHandle {} does not exists".format(id))
        agentNetwork = getAgentNetwork(id, networkId)
        if agentNetwork :
            abort(404, message="agentNetwork already exist with agent {} and network {}".format(id,networkId))
        agentNetwork = cls.AgentNetwork()
        agentNetwork.agentHandleId = id
        agentNetwork.networkId = networkId
        session.add(agentNetwork)
        session.commit()
        return agentNetwork
        
    
    

class NetworkResource(Resource):
    
    def get(self):
        networks = session.query(cls.Network).all()
        fields = request.args.get('fields')
        networksToShow = []
        for network in networks :
            networksToShow.append(networkString(network,fields))
        return networksToShow
        
    
    def post(self):
        postData = request.data
        description = ''
        networkProtocol = ''
        agent = None
        memberNetworks = []
        if postData != '' and postData != None :
            postDataJSON = json.loads(postData)
            try :
                agentId = postDataJSON['creator']
                agent = getAgent(agentId)
                if not agent :
                    abort(404, message="creator does not exists".format(agentId))
            except KeyError :
                abort(404, message="creator is required")
                
            try :
                description = postDataJSON['description']
            except KeyError :
                abort(404, message="description is required")
                
            try :
                name = postDataJSON['name']
            except KeyError :
                abort(404, message="name is required")
                
            try :
                networkProtocol = postDataJSON['networkProtocol']
            except KeyError :
                abort(404, message="protocol is required")
                
            try :
                agents = postDataJSON['agents']
                for agentId in agents:
                    memberNetwork = getAgent(agentId)
                    if not memberNetwork :
                        abort(404, message="member agent does not exists".format(agentId))
                    memberNetworks.append(memberNetwork)
            except KeyError :
                memberNetworks = []
        
        network = cls.Network()
        network.name = name
        network.description = description
        network.agentId = agent.id
        if networkProtocol == '' or networkProtocol == None:
            abort(404, message="protocol is required")
        network.protocol = json.dumps(networkProtocol)
        
        session.add(network)
        session.flush()
        
        for memberNetwork in memberNetworks :
            agentNetwork = cls.AgentNetwork()
            agentNetwork.agentId = memberNetwork.id
            agentNetwork.networkId = network.id
            session.add(agentNetwork)
            
        session.commit()
        return {"id":network.id}, 201
    
class NetworkParameterResource(Resource):
    
    def get(self, id):
        network = session.query(cls.Network).filter(cls.Network.id == id).first()
        if not network :
            abort(404, message="Network {} does not exists".format(id))
        fields = request.args.get('fields')
        networksToShow = networkString(network,fields)
        return networksToShow
    
    

    
class CollaborationResource(Resource):
    
    def get(self):
        networkId = request.args.get('networkId')
        agentId = request.args.get('agentId')
        if(networkId != None and agentId == None) :
            network = session.query(cls.Network).filter(cls.Network.id == networkId).first()
            if not network :
                abort(404, message="Network {} does not exists".format(networkId))
            collaborations = network.collaborations
        
        elif(networkId != None and agentId != None) :
            network = session.query(cls.Network).filter(cls.Network.id == networkId).first()
            if not network :
                abort(404, message="Network {} does not exists".format(networkId))
            allcollaborations = network.collaborations
            collaborations = []
            for collaboration in allcollaborations :
                agentCollaborations = collaboration.agentCollaborations
                for agentCollaboration in agentCollaborations :
                    if int(agentCollaboration.agentHandleId) == int(agentId) :
                        collaborations.append(collaboration)
                        break
                        
        else :
            collaborations = session.query(cls.Collaboration).all()       
        fields = request.args.get('fields')
        collaborationsToShow = []
        for collaboration in collaborations :
            collaborationsToShow.append(collaborationString(collaboration,fields))
        return collaborationsToShow
    
    def delete(self):
        networkId = request.args.get('networkId')
        if(networkId != None ) :
            network = session.query(cls.Network).filter(cls.Network.id == networkId).first()
            if not network :
                abort(404, message="Network {} does not exists".format(networkId))
            collaborations = network.collaborations
        else :
            collaborations = session.query(cls.Collaboration).all()
            
        for collaboration in collaborations :
            deleteCollaboration(collaboration)
        session.commit()
        return "Collaborations deleted successfully", 200
    
    
    def post(self):
        postData = request.data
        description = ''
        network = None
        agent = None
        collaboration = cls.Collaboration()
        if postData != '' and postData != None :
            postDataJSON = json.loads(postData)
            try :
                agentId = postDataJSON['creator']
                agent = getAgent(agentId)
                if not agent :
                    abort(404, message="creator does not exists".format(agentId))
            except KeyError :
                abort(404, message="creator is required")
            collaboration.agentId = agent.id
            try :
                networkId = postDataJSON['network']
                network = getNetwork(networkId)
                if not network :
                    abort(404, message="network {} doesn't exist".format(networkId))
            except KeyError :
                abort(404, message="network is required")
            collaboration.networkId = network.id 
                
            try :
                description = postDataJSON['description']
            except KeyError :
                abort(404, message="description is required")
            collaboration.description = description
            
            try :
                name = postDataJSON['name']
            except KeyError :
                abort(404, message="name is required")
            collaboration.name = name
            
            try :
                comment = postDataJSON['comment']
                collaboration.comment = comment
            except KeyError :
                comment = ''
                
            
            try :
                token = postDataJSON['token']
                collaboration.tokenName = token['name']
                collaboration.tokenSymbol = token['symbol']
                collaboration.tokenTotal = token['total']
            except KeyError :
                abort(404, message="Tokens is required")
                
            try :
                collaborationProtocol = postDataJSON['collaborationProtocol']
                if collaborationProtocol != '' or collaborationProtocol != None :
                    try:
                        type = collaborationProtocol['type']
                        parameters = collaborationProtocol['parameters']
                        collaboration.protocol = json.dumps(collaborationProtocol)
                    except KeyError :
                        abort(404, message="collaborationProtocol type and parameters is required")
                    
                
            except KeyError :
                collaborationProtocol = ''
                
                
            session.add(collaboration)
            session.flush()
                
            try :
                contributors = postDataJSON['contributors']
                for contributor in contributors:
                    agentNetwork = getAgentNetwork(contributor['id'], network.id)
                    if not agentNetwork :
                        abort(404, message="contributor {} does not exists in network {}".format(contributor['id'],network.id))
                    agentCollaboration = cls.AgentCollaboration()
                    agentCollaboration.collaborationId = collaboration.id
                    agentCollaboration.agentId = agentNetwork.agent.id
                    agentCollaboration.tokens = int(collaboration.tokenTotal)*float(contributor['ownership'])
                    agentCollaboration.reputation = int(collaboration.tokenTotal)*float(contributor['ownership'])
                    session.add(agentCollaboration)
                if len(contributors) == 0 :
                    agentCollaboration = cls.AgentCollaboration()
                    agentCollaboration.collaborationId = collaboration.id
                    agentCollaboration.agentId = agent.id
                    agentCollaboration.tokens = collaboration.tokenTotal
                    agentCollaboration.reputation = collaboration.tokenTotal
                    session.add(agentCollaboration)
            except KeyError :
                agentCollaboration = cls.AgentCollaboration()
                agentCollaboration.collaborationId = collaboration.id
                agentCollaboration.agentId = agent.id
                agentCollaboration.tokens = collaboration.tokenTotal
                agentCollaboration.reputation = collaboration.tokenTotal
                session.add(agentCollaboration)
                
            try :
                handles = postDataJSON['handles']
                for handle in handles:
                    collaborationHandle = cls.CollaborationHandle()
                    collaborationHandle.collaborationId = collaboration.id
                    collaborationHandle.handleName = handle['name']
                    collaborationHandle.handleType = handle['type']
                    session.add(collaborationHandle)
            except KeyError :
                handles = ''
        
            #submit founding contribution
            
        session.commit()    
        return {"id":collaboration.id}, 201
    
class GetCollaborationsByNetworkResource(Resource):
    
    def get(self, id):
        collaborations = session.query(cls.Collaboration).filter(cls.Collaboration.networkId == id).all()
        fields = request.args.get('fields')
        collaborationsToShow = []
        for collaboration in collaborations :
            collaborationsToShow.append(collaborationString(collaboration,fields))
        return collaborationsToShow
    

class GetCollaborationsByAgentResource(Resource):
    
    def get(self, id):
        agent = getAgent(id)
        if not agent :
            abort(404, message="Agent {} does not exists".format(id))
        networkId = request.args.get('networkId')
        if networkId != None and networkId != '' :
            network = getNetwork(networkId)
            if not network :
                abort(404, message="network {} does not exists".format(networkId))
            collaborations = session.query(cls.Collaboration).filter(cls.Collaboration.networkId == networkId).filter(cls.Collaboration.agentId == id).all()
        else :
            collaborations = session.query(cls.Collaboration).filter(cls.Collaboration.agentId == id).all()
        fields = request.args.get('fields')
        collaborationsToShow = []
        for collaboration in collaborations :
            collaborationsToShow.append(collaborationString(collaboration,fields))
        return collaborationsToShow
    
class GetContributionByAgentResource(Resource):
    
    def get(self, id):
        agent = getAgent(id)
        if not agent :
            abort(404, message="Agent {} does not exists".format(id))
        collaborationId = request.args.get('collaborationId')
        if collaborationId != None and collaborationId != '' :
            collaboration = getCollaboration(id)
            if not collaboration :
                abort(404, message="collaborationId {} does not exists".format(collaborationId))
            contributions = session.query(cls.Contribution).filter(cls.Contribution.agentCollaborationId == cls.AgentCollaboration.id).filter(cls.AgentCollaboration.agentId == id).filter(cls.AgentCollaboration.collaborationId == collaboration.id).all()
        else :
            contributions = session.query(cls.Contribution).filter(cls.Contribution.agentCollaborationId == cls.AgentCollaboration.id).filter(cls.AgentCollaboration.agentId == id).all()
        fields = request.args.get('fields')
        contributionssToShow = []
        for contribution in contributions :
            contributionssToShow.append(contributionString(contribution,fields))
        return contributionssToShow
    
   
    
class GetContributionByCollaborationResource(Resource):
    
    def get(self, id):
        collaboration = getCollaboration(id)
        if not collaboration :
            abort(404, message="collaborationId {} does not exists".format(id))
        contributions = session.query(cls.Contribution).filter(cls.Contribution.agentCollaborationId == cls.AgentCollaboration.id).filter(cls.AgentCollaboration.collaborationId == id).all()
        fields = request.args.get('fields')
        contributionssToShow = []
        for contribution in contributions :
            contributionssToShow.append(contributionString(contribution,fields))
        return contributionssToShow
    
    
class CollaborationParameterResource(Resource):
    
    def get(self, id):
        collaboration = getCollaboration(id)
        if not collaboration :
            abort(404, message="collaborationId {} does not exists".format(id))
        fields = request.args.get('fields')
        return collaborationString(collaboration,fields)
    
    def delete(self, id):
        collaboration = session.query(cls.Collaboration).filter(cls.Collaboration.id == id).first()
        if collaboration :
            deleteCollaboration(collaboration)            
            session.commit()
        return "Collaboration deleted successfully", 200
    
    
    
class CollaborationClose(Resource):

    @marshal_with(contribution_fields)
    def put(self):
        collaborationId = request.args.get('id')
        collaboration = session.query(cls.Collaboration).filter(cls.Collaboration.id == collaborationId).first()
        if not collaboration :
            abort(404, message="collaborationId {} does not exists".format(collaborationId)) 
        contributions = collaboration.contributions 
        winningContribution = None
        maxContributionValueAfterEvaluation = 0
        for contribution in contributions :
            if contribution.contributionValueAfterEvaluation > maxContributionValueAfterEvaluation :
                maxContributionValueAfterEvaluation = contribution.contributionValueAfterEvaluation
                winningContribution = contribution
            contribution.status = 'Closed'
            session.add(contribution) 
        collaboration.status = 'Closed'
        session.add(collaboration) 
        session.commit()
        return winningContribution, 200
    
class ContributionResource(Resource):
    def get(self):
        key = request.args.get('key')
        contains = request.args.get('contains')
        if key != '' and  key != None and contains != '' and  contains != None :
            allContributions = session.query(cls.Contribution).all()
            contributions = []
            for contribution in allContributions:
                content = contribution.content
                handlesContent = json.loads(content)
                try :
                    keyValues = handlesContent[key]
                    if not isinstance(keyValues, (list)):
                        if contains in keyValues:
                            contributions.append(contribution)
                    else:
                        for keyValue in keyValues :
                            if contains in keyValue:
                                contributions.append(contribution)
                                break
                    
                    
                except KeyError :
                    keyValue = ''
        else :
            contributions = session.query(cls.Contribution).all()            
        
        fields = request.args.get('fields')
        contributionssToShow = []
        for contribution in contributions :
            contributionssToShow.append(contributionString(contribution,fields))
        return contributionssToShow

    def delete(self):
        contributions = session.query(cls.Contribution).all()
        for contribution in contributions :
            deleteContribution(contribution)
        session.commit()
        return "Contributions deleted successfully", 200
    
    def post(self): 
        type = None
        agent = None
        collaboration = None
        agentCollaboration = None
        postData = request.data
        contribution = cls.Contribution()
        if postData != '' and postData != None :
            postDataJSON = json.loads(postData)
            try :
                agentId = postDataJSON['creator']
                agent = getAgent(agentId)
                if not agent :
                    abort(404, message="creator does not exists".format(agentId))
                contribution.agentId = agent.id
            except KeyError :
                abort(404, message="creator is required")
                
            try :
                collaborationId = postDataJSON['collaboration']
                collaboration = session.query(cls.Collaboration).filter(cls.Collaboration.id == collaborationId).first()
                if not collaboration :
                    abort(404, message="Collaboration {} does not exists".format(collaborationId))
                    
                agentCollaboration = getAgentCollaboration(agent.id,collaboration.id)
                if not agentCollaboration :
                    abort(404, message="Agent {} does not exists in Collaboration {} ".format(agent.id,collaborationId)) 
                contribution.agentCollaborationId = agentCollaboration.id
            except KeyError :
                abort(404, message="collaboration is required")
                
            try :
                comment = postDataJSON['comment']
                contribution.comment = comment
            except KeyError :
                comment = ''
                
            try :
                type = postDataJSON['type']
                contribution.type = type
            except KeyError :
                abort(404, message="Type is required")
                
            session.add(contribution)    
            session.flush()
                
            try :
                content = postDataJSON['content']
                if type == 'qrate':
                    linkName = content['url']
                    tags = content['tags']
                    link = getLINK(linkName)
                    if not link :
                        link = cls.LINK()
                        link.name = linkName
                        session.add(link)    
                        session.flush()
                    for tagName in tags:
                        tag = getTag(tagName)
                        if not tag:
                            tag = cls.Tag()
                            tag.name = tagName
                            session.add(tag)    
                            session.flush()
                        tagLINK = cls.TagLINK()
                        tagLINK.tagId = tag.id
                        tagLINK.linkId = link.id
                        tagLINK.contributionId = contribution.id
                        session.add(tagLINK)    
                        session.flush()
                            
                if type == 'milestone':
                    contributions = content['contributions']
                    for contribution in contributions:
                        if not getCollaborationContribution(contribution.id, collaboration.id) :
                            abort(404, message="contribution {} does not exist in collaboration".format(contribution.id,collaboration.id)) 
                    submitter = content['submitter']
                    submitterCoolaboration = session.query(cls.Collaboration).filter(cls.Collaboration.id == submitter).filter(cls.Collaboration.networkId == collaboration.networkId).first()
                    if submitterCoolaboration == None :
                        abort(404, message="submitterCoolaboration {} does not exist".format(submitter)) 
                contribution.content = json.dumps(content)
            except KeyError :
                abort(404, message="content is required") 
                
            
            try :
                contributors = postDataJSON['contributors']
                for contributor in contributors:
                    agentCollaboration = getAgentCollaboration(contributor['id'], collaboration.id)
                    if not agentCollaboration :
                        abort(404, message="contributor {} does not exists in Collaboration {}".format(contributor['id'],collaboration.id))
                    contributionContributor = cls.ContributionContributor()
                    contributionContributor.contributorId = agentCollaboration.agentId
                    contributionContributor.percentage = float(contributor['ownership'])*100
                    contributionContributor.contributionId = contribution.id
                    session.add(contributionContributor)    
                    
                if len(contributors) == 0 :
                    contributionContributor = cls.ContributionContributor()
                    contributionContributor.contributorId = agent.id
                    contributionContributor.percentage = 100
                    contributionContributor.contributionId = contribution.id
                    session.add(contributionContributor) 
            except KeyError :
                    contributionContributor = cls.ContributionContributor()
                    contributionContributor.contributorId = agent.id
                    contributionContributor.percentage = 100
                    contributionContributor.contributionId = contribution.id
                    session.add(contributionContributor)
                
        #adding reputation stats for this contribution
        agentCollaborations = session.query(cls.AgentCollaboration).filter(cls.AgentCollaboration.collaborationId == collaboration.id).all()
        for agentCollaboration in agentCollaborations :
              contributionValue = cls.ContributionValue()
              contributionValue.agentId = agentCollaboration.agentId
              contributionValue.agentCollaborationId = agentCollaboration.id
              contributionValue.contributionId = contribution.id
              contributionValue.reputationGain = 0
              contributionValue.reputation = agentCollaboration.reputation
              session.add(contributionValue)
              
        session.commit()    
        
        return {"id":contribution.id}, 201
    
class ContributionParameterResource(Resource):
    def get(self, id):
        contribution = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        if not contribution:
            abort(404, message="Contribution {} doesn't exist".format(id))
        fields = request.args.get('fields')
        contribution = contributionString(contribution,fields)
        return contribution

    def delete(self, id):
        contribution = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        if not contribution:
            abort(404, message="Contribution {} doesn't exist".format(id))
        deleteContribution(contribution)
        session.commit()
        return "Contribution deleted successfully", 200
    

class EvaluationResource(Resource):

    def post(self):
        evaluation = cls.Evaluation() 
        postData = request.data
        agent = None
        contribution = None
        if postData != '' and postData != None :
            postDataJSON = json.loads(postData)
            try :
                agentId = postDataJSON['creator']
                agent = getAgent(agentId)
                if not agent :
                    abort(404, message="creator does not exists".format(agentId))
                evaluation.agentId = agent.id
            except KeyError :
                abort(404, message="creator is required")
               
            try :
                evaluationToken = postDataJSON['evaluation']
                evaluation.tokens = evaluationToken
            except KeyError :
                abort(404, message="evaluation is required") 
                
            try :
                comment = postDataJSON['comment']
                evaluation.comment = comment
            except KeyError :
                comment = ''
                
            try :
                stake = postDataJSON['stake']
                evaluation.stake = stake
            except KeyError :
                abort(404, message="stake is required") 
                
            try :
                contributionId = postDataJSON['contributionId']
                contribution = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
                if not contribution :
                    abort(404, message="contributionId {} does not exists".format(id))
                evaluation.contributionId = contribution.id        
            except KeyError :
                abort(404, message="stake is required") 
                
        
        
           
        
        if contribution.status != 'Open':
            abort(404, message="Contribution {} is not Open".format(id))
        contributionValues = session.query(cls.ContributionValue).filter(cls.ContributionValue.contributionId == contribution.id).filter(cls.ContributionValue.agentCollaborationId == cls.AgentCollaboration.id).filter(cls.AgentCollaboration.agentId == agent.id).filter(cls.AgentCollaboration.collaborationId == contribution.agentCollaboration.collaborationId).first()
        evaluation.reputation = contributionValues.reputation
        previousTokens = getAgentCollaboration(agent.id, contribution.agentCollaboration.collaborationId).tokens
        vd = ValueDistributer('ProtocolFunctionV1')
        vd.process_evaluation(evaluation,session)
        if(vd.error_occured):
            print vd.error_code
            # ToDo :  pass correct error message to agent
            abort(404, message="Failed to process evaluation {} due to"+vd.error_code.format(contribution.id))
        fields = request.args.get('fields')
        currentTokens = getAgentCollaboration(agent.id, contribution.agentCollaboration.collaborationId).tokens
        diffrenceTokens = currentTokens - previousTokens
        return evaluationString(evaluation,fields,diffrenceTokens), 201
    
class EvaluationParameterResource(Resource):
    def get(self, id):
        fields = request.args.get('fields')
        evaluation = session.query(cls.Evaluation).filter(cls.Evaluation.id == id).first()
        if not evaluation:
            abort(404, message="EvaluationId {} doesn't exist".format(id))
        return evaluationString(evaluation,fields,'')

    def delete(self, id):
        evaluation = session.query(cls.Evaluation).filter(cls.Evaluation.id == id).first()
        if not evaluation:
            abort(404, message="EvaluationId {} doesn't exist".format(id))
        session.delete(evaluation)
        session.commit()
        return "Evaluation deleted successfully", 200
    
class GetEvaluationForContributionResource(Resource):
    def get(self, id):
        fields = request.args.get('fields')
        contribution = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        if not contribution:
            abort(404, message="Contribution {} doesn't exist".format(id))
        evaluations = contribution.evaluations
        evaluationsToShow = []
        for evaluation in evaluations :
            evaluationsToShow.append(evaluationString(evaluation,fields,''))
        return evaluationsToShow

    def delete(self, id):
        evaluation = session.query(cls.Evaluation).filter(cls.Evaluation.id == id).first()
        if not evaluation:
            abort(404, message="EvaluationId {} doesn't exist".format(id))
        session.delete(evaluation)
        session.commit()
        return "Evaluation deleted successfully", 200


class AllTagsResource(Resource):
    
    @marshal_with(tag_fields)
    def get(self):
        query = request.args.get('query')
        tags = []
        excludeTagsNames = request.args.get('excludeTagsNames')
        if query != '' and query != None and excludeTagsNames != '' and excludeTagsNames != None :
            excludeTagsNamesList = excludeTagsNames.split(",")
            tags = session.query(cls.Tag).filter(cls.Tag.name.like('%'+query+'%')).filter(cls.Tag.name.notin_(excludeTagsNamesList)).all()
        elif (query == '' or query == None) and excludeTagsNames != '' and excludeTagsNames != None :
            excludeTagsNamesList = excludeTagsNames.split(",")
            tags = session.query(cls.Tag).filter(cls.Tag.name.notin_(excludeTagsNamesList)).all()
        elif query != '' and query != None and (excludeTagsNames == '' or excludeTagsNames == None) :
            tags = session.query(cls.Tag).filter(cls.Tag.name.like('%'+query+'%')).all()
        else :
            tags = session.query(cls.Tag).all()
        
        return tags
    
class GetLinksByTagResource(Resource):
    
    def get(self):
        tagName = request.args.get('tag')
        if tagName == '' and tagName == None :
            abort(404, message="tagName is required")
        tagLINKs = session.query(cls.TagLINK).filter(cls.TagLINK.tagId == cls.Tag.id).filter(cls.Tag.name == tagName).all()
        titles = []
        contributionIds = {}
        for tagLINK in tagLINKs :
            contribution = tagLINK.contribution
            try :
                contributionIds[contribution.id]
            except KeyError :
                contributionIds[contribution.id] = contribution.id
                titles.append(json.loads(contribution.content)['title'])
        return titles
    
class GetTagsByLinkResource(Resource):
    
    @marshal_with(tag_fields)
    def get(self):
        linkName = request.args.get('url')
        if linkName == '' and linkName == None :
            abort(404, message="url is required")
        tags = session.query(cls.Tag).filter(cls.TagLINK.tagId == cls.Tag.id).filter(cls.TagLINK.linkId == cls.LINK.id).filter(cls.LINK.name == linkName).all()
        return tags
    
class GetLinksANDTagsResource(Resource):
    
    def get(self):
        query = request.args.get('query')
        if query == '' and query == None :
            abort(404, message="query is required")
        taglinks = []
        taglinks.extend(session.query(cls.TagLINK).filter(cls.TagLINK.linkId == cls.LINK.id).filter(cls.LINK.name.like('%'+query+'%')).all())
        taglinks.extend(session.query(cls.TagLINK).filter(cls.TagLINK.tagId == cls.Tag.id).filter(cls.Tag.name.like('%'+query+'%')).all())
        titles = []
        contributionIds = {}
        for tagLINK in taglinks :
            contribution = tagLINK.contribution
            try :
                contributionIds[contribution.id]
            except KeyError :
                contributionIds[contribution.id] = contribution.id
                titles.append(json.loads(contribution.content)['title'])
        return titles
    

        
        
    
class CollaborationStatsForContributionsResource(Resource):
    
    @marshal_with(contribution_fields)
    def get(self, id):
        collaboration = session.query(cls.Collaboration).filter(cls.Collaboration.id == id).first()
        if not collaboration :
            abort(404, message="collaborationId {} does not exists".format(id))
        collaborationContributions = session.query(cls.Contribution).filter(cls.Contribution.agentCollaborationId == cls.AgentCollaboration.id).filter(cls.Contribution.AgentCollaboration.collaborationId == cls.Collaboration.id).all()
        return collaborationContributions
    
class CollaborationStatsForEvaluationsResource(Resource):
    
    @marshal_with(evaluation_fields)
    def get(self, id):
        collaboration = session.query(cls.Collaboration).filter(cls.Collaboration.id == id).first()
        if not collaboration :
            abort(404, message="collaborationId {} does not exists".format(id))
        collaborationEvaluations = session.query(cls.Evaluation).filter(cls.Evaluation.contributionId == cls.Contribution.id).filter(cls.Contribution.agentCollaborationId == cls.AgentCollaboration.id).filter(cls.Contribution.AgentCollaboration.collaborationId == cls.Collaboration.id).all()
        return collaborationEvaluations
    
class AgentStatsForContributionsResource(Resource):
    
    @marshal_with(contribution_fields)
    def get(self, id):
        agent = session.query(cls.Agent).filter(cls.Agent.id == id).first()
        if not agent :
            abort(404, message="agentId {} does not exists".format(id))
        agentContributions = session.query(cls.Contribution).filter(cls.Contribution.agentCollaborationId == cls.AgentCollaboration.id).filter(cls.Contribution.AgentCollaboration.agentId == cls.Agent.id).all()
        return agentContributions
    
class AgentStatsForEvaluationsResource(Resource):
    
    @marshal_with(evaluation_fields)
    def get(self, id):
        agent = session.query(cls.Agent).filter(cls.Agent.id == id).first()
        if not agent :
            abort(404, message="agentId {} does not exists".format(id))
        agentEvaluations = session.query(cls.Evaluation).filter(cls.Evaluation.contributionId == cls.Contribution.id).filter(cls.Contribution.agentCollaborationId == cls.AgentCollaboration.id).filter(cls.Contribution.AgentCollaboration.agentId == cls.Agent.id).all()
        return agentEvaluations
    

def agentString(agent,fields):
    data = {}
    try :
        if fields == '' or fields == None :
            data['name'] = agent.name
            data['id'] = agent.id
            data['handles'] = []
            data['networks'] = []
            data['collaborations'] = []
            data['contributions'] = []
            for handle in agent.agentHandles:
                dataHandles = handleString(handle,None)
                data['handles'].append(dataHandles)
            for agentNetwork in agent.agentNetworks:
                dataNetworks = networkString(agentNetwork.network,None)
                data['networks'].append(dataNetworks)
            for agentCollaboration in agent.agentCollaborations:
                dataCollaborations = collaborationString(agentCollaboration.collaboration,None)
                dataCollaborations['tokens'] = agentCollaboration.tokens
                dataCollaborations['reputation'] = agentCollaboration.reputation
                data['collaborations'].append(dataCollaborations)
            for contribution in agent.agentContributions:
                dataContributions = contributionString(contribution,None)
                data['contributions'].append(dataContributions)        
        else :
            fieldSet = fields.split(',')
            for field in fieldSet :
                fieldSet1 = field.split('.',1)
                if fieldSet1[0] == 'networks' :
                    data['networks'] = []
                    if(len(fieldSet1) == 1) :
                        fieldSetForNetwork = None
                    else :
                        fieldSetForNetwork = fieldSet1[1]
                    for agentNetwork in agent.agentNetworks:
                        dataNetworks = networkString(agentNetwork.network,fieldSetForNetwork)
                        data['networks'].append(dataNetworks)
                        
                elif fieldSet1[0] == 'handles' :
                    data['handles'] = []
                    if(len(fieldSet1) == 1) :
                        fieldSetForHandle = None
                    else :
                        fieldSetForHandle = fieldSet1[1]
                    for handle in agent.agentHandles:
                        dataHandles = handleString(handle,fieldSetForHandle)
                        data['handles'].append(dataHandles) 
                        
                elif fieldSet1[0] == 'collaborations' :
                    data['collaborations'] = []
                    if(len(fieldSet1) == 1) :
                        fieldSetFoCollaboration = None
                    else :
                        fieldSetFoCollaboration = fieldSet1[1]
                    for agentCollaboration in agent.agentCollaborations:
                        dataCollaborations = collaborationString(agentCollaboration.collaboration,fieldSetFoCollaboration)
                        if fieldSetFoCollaboration == 'tokens' :
                            dataCollaborations['tokens'] = agentCollaboration.tokens
                        if fieldSetFoCollaboration == 'reputation' :
                            dataCollaborations['reputation'] = agentCollaboration.reputation
                        if fieldSetFoCollaboration == None :
                            dataCollaborations['tokens'] = agentCollaboration.tokens
                            dataCollaborations['reputation'] = agentCollaboration.reputation
                        data['collaborations'].append(dataCollaborations)
                        
                elif fieldSet1[0] == 'contributions' :
                    data['contributions'] = []
                    if(len(fieldSet1) == 1) :
                        fieldSetFoContribution = None
                    else :
                        fieldSetFoContribution = fieldSet1[1]
                    for contribution in agent.agentContributions:
                        dataContributions = contributionString(contribution,fieldSetFoContribution)
                        data['contributions'].append(dataContributions)
                
                else :
                    data[field] = agent.__dict__[field]
    except :
            print 'Could not get data from agent.'
        
    return data

def evaluationString(evaluation,fields,diffrenceTokens):
    try:
        data = {}
        if fields == '' or fields == None :
            data['id'] = evaluation.id
            data['agentId'] = evaluation.agentId
            data['contributionId'] = evaluation.contributionId
            data['evaluation'] = evaluation.tokens
            data['stake'] = evaluation.stake
            data['comment'] = evaluation.comment
            if diffrenceTokens != '' :
                data['senderTokenReputationChange'] = diffrenceTokens
            data['contributionNewValue'] = evaluation.contributionValueAfterEvaluation
        else :
            fieldSet = fields.split(',')
            for field in fieldSet :
                print 'field'+field+str(field == 'contributionNewValue')
                if field.strip() == 'senderTokenReputationChange':
                    if diffrenceTokens != '':
                        data[field.strip()] = diffrenceTokens
                elif field.strip() == 'contributionNewValue' :
                    data[field.strip()] = evaluation.contributionValueAfterEvaluation
                elif field.strip() == 'evaluation' :
                    data[field.strip()] = evaluation.tokens
                else :
                    data[field.strip()] = evaluation.__dict__[field.strip()]
    except :
            print 'Could not get data from evaluation.'
            
    return data

def networkString(network,fields):
    try :
        data = {}
        if fields == '' or fields == None :
            data['id'] = network.id
            data['agentId'] = network.agentId
            data['name'] = network.name
            data['description'] = network.description
            data['protocol'] = json.loads(network.protocol)
        else :
            fieldSet = fields.split(',')
            for field in fieldSet :
                if field == 'protocol' :
                    data[field] = json.loads(network.protocol)
                elif field == 'collaborations' :
                    data[field] = []
                    for collaboration in network.collaborations:
                        dataContributors = collaborationString(collaboration,None)
                        data[field].append(dataContributors)
                elif 'collaborations' in field :
                    fields1 = field.split('.',1)
                    data['collaborations'] = []
                    for collaboration in network.collaborations:
                        dataContributors = collaborationString(collaboration,fields1[1])
                        data['contributors'].append(dataContributors)
                else :
                    data[field] = network.__dict__[field]
            
    except :
            print 'Could not get data from network.'  
    return data

def handleString(handle,fields):
    try:
        data = {}
        if fields == '' or fields == None :
            data['type'] = handle.handleType
            data['name'] = handle.handleName
        else :
            fieldSet = fields.split(',')
            for field in fieldSet :
                if field == 'type' :
                    data['type'] = handle.handleType
                elif field == 'name' :
                    data['name'] = handle.handleName
                else :    
                    data[field] = handle.__dict__[field]
    except :
            print 'Could not get data from handle.' 
            
        
    return data

def collaborationString(collaboration,fields):
    try:
        data = {}
        if fields == '' or fields == None :
            data['id'] = collaboration.id
            data['agentId'] = collaboration.agentId
            data['networkId'] = collaboration.networkId
            data['tokenName'] = collaboration.tokenName
            data['name'] = collaboration.name
            data['description'] = collaboration.description
            data['tokenSymbol'] = collaboration.tokenSymbol
            data['tokenTotal'] = collaboration.tokenTotal
            data['comment'] = collaboration.comment
            data['status'] = collaboration.status
            data['protocol'] = json.loads(collaboration.protocol)
            data['handles'] = []
            for handle in collaboration.handles:
                datahandles = {}
                datahandles['handleName'] = handle.handleName
                datahandles['handleType'] = handle.handleType
                data['handles'].append(datahandles)
            data['contributors'] = []
            for contributor in collaboration.agentCollaborations:
                dataContributors = {}
                dataContributors['id'] = contributor.id
                dataContributors['agentId'] = contributor.agentId
                dataContributors['tokens'] = contributor.tokens
                dataContributors['reputation'] = contributor.reputation
                data['contributors'].append(dataContributors)
        else :
            fieldSet = fields.split(',')
            for field in fieldSet :
                if field == 'protocol' :
                    data[field] = json.loads(collaboration.protocol)
                elif field == 'handles' :
                    data[field] = []
                    for handle in collaboration.handles:
                        datahandles = {}
                        datahandles['handleName'] = handle.handleName
                        datahandles['handleType'] = handle.handleType
                        data[field].append(datahandles)
                elif 'handles' in field :
                    fields1 = field.split('.')
                    data['handles'] = []
                    for handle in collaboration.handles:
                        datahandles = {}
                        datahandles[fields1[1]] = handle.__dict__[fields1[1]]
                        data['handles'].append(datahandles)
                elif field == 'contributors' :
                    data[field] = []
                    for contributor in collaboration.agentCollaborations:
                        dataContributors = {}
                        dataContributors['id'] = contributor.id
                        dataContributors['agentId'] = contributor.agentId
                        dataContributors['tokens'] = contributor.tokens
                        dataContributors['reputation'] = contributor.reputation
                        data[field].append(dataContributors)
                elif 'contributors' in field :
                    fields1 = field.split('.')
                    data['contributors'] = []
                    for contributor in collaboration.agentCollaborations:
                        dataContributors = {}
                        dataContributors[fields1[1]] = contributor.__dict__[fields1[1]]
                        data['contributors'].append(dataContributors)
                else :
                    data[field] = collaboration.__dict__[field]
    
    except :
            print 'Could not get data from collaboration.' 
            
        
    return data

def contributionString(contribution,fields):
    try: 
        data = {}
        dataContributors = {}
        if fields == '' or fields == None :
            data['id'] = contribution.id
            data['agentId'] = contribution.agentId
            data['agentCollaborationId'] = contribution.agentCollaborationId
            data['comment'] = contribution.comment
            data['type'] = contribution.type
            data['status'] = contribution.status
            data['content'] = json.loads(contribution.content)
            data['contributors'] = []
            for contributor in contribution.contributors:
                dataContributors = {}
                dataContributors['id'] = contributor.id
                dataContributors['contributionId'] = contributor.contributionId
                dataContributors['contributorId'] = contributor.contributorId
                dataContributors['ownership'] = contributor.percentage/100
                data['contributors'].append(dataContributors)
        else :
            fieldSet = fields.split(',')
            for field in fieldSet :
                if field == 'content' :
                    data[field] = json.loads(contribution.content)
                elif field == 'contributors' :
                    data[field] = []
                    for contributor in contribution.contributors:
                        dataContributors = {}
                        dataContributors['id'] = contributor.id
                        dataContributors['contributionId'] = contributor.contributionId
                        dataContributors['contributorId'] = contributor.contributorId
                        dataContributors['ownership'] = contributor.percentage/100
                        data[field].append(dataContributors)
                elif 'contributors' in field :
                    fields1 = field.split('.')
                    data['contributors'] = []
                    for contributor in contribution.contributors:
                        dataContributors = {}
                        if fields1[1] == 'ownership' :
                            dataContributors[fields1[1]] = contributor.percentage/100
                        else :
                            dataContributors[fields1[1]] = contributor.__dict__[fields1[1]]
                    
                        data['contributors'].append(dataContributors)
                else :
                    data[field] = contribution.__dict__[field]
    except :
            print 'Could not get data from contribution.'       
        
    return data
            
    

def getCollaboration(id):
    collaboration = session.query(cls.Collaboration).filter(cls.Collaboration.id == id).first()    
    return collaboration

def getAgent(id):
    agent = session.query(cls.Agent).filter(cls.Agent.id == id).first()    
    return agent 

def getLINK(name):
    link = session.query(cls.LINK).filter(cls.LINK.name == name).first()    
    return link

def getTag(name):
    tag = session.query(cls.Tag).filter(cls.Tag.name == name).first()    
    return tag

def getTaglink(tagId,linkId):
    tagLINK = session.query(cls.TagLINK).filter(cls.TagLINK.tagId == tagId).filter(cls.TagLINK.linkId == linkId).first()    
    return tagLINK

def getNetwork(id):
    network = session.query(cls.Network).filter(cls.Network.id == id).first()    
    return network



def getByAgentAndHandle(id,handleId):
    agentHandle = session.query(cls.AgentHandle).filter(cls.AgentHandle.agentId == id).filter(cls.AgentHandle.handleId == handleId).first()    
    return agentHandle

def getByHandle(handleId):
    agentHandles = session.query(cls.AgentHandle).filter(cls.AgentHandle.handleId == handleId).first()    
    return agentHandles

def getAgentHandle(id):
    agentHandle = session.query(cls.AgentHandle).filter(cls.AgentHandle.id == id).first()    
    return agentHandle

def getAgentByName(name):
    agent = session.query(cls.Agent).filter(cls.Agent.name == name).first()    
    return agent

def getAgentByNameAndType(name,handleName,handleType):
    agentHandle = session.query(cls.AgentHandle).filter(cls.Agent.name == name).filter(cls.AgentHandle.agentId == cls.Agent.id).filter(cls.AgentHandle.handleName == handleName).filter(cls.AgentHandle.handleType == handleType).first()    
    return agentHandle

def getAgentByHandleNameAndType(handleName,handleType):
    agentHandle = session.query(cls.AgentHandle).filter(cls.AgentHandle.handleName == handleName).filter(cls.AgentHandle.handleType == handleType).first()    
    return agentHandle

def getAgentByIdAndType(id,handleName,handleType):
    agentHandle = session.query(cls.AgentHandle).filter(cls.Agent.id == id).filter(cls.AgentHandle.agentId == cls.Agent.id).filter(cls.AgentHandle.handleName == handleName).filter(cls.AgentHandle.handleType == handleType).first()    
    return agentHandle

def getAgentNetwork(agentId,networkId):
    agentNetwork = session.query(cls.AgentNetwork).filter(cls.AgentNetwork.agentId == agentId).filter(cls.AgentNetwork.networkId == networkId).first()    
    return agentNetwork

def getAgentCollaboration(agentId,collaborationId):
    agentCollaboration = session.query(cls.AgentCollaboration).filter(cls.AgentCollaboration.agentId == agentId).filter(cls.AgentCollaboration.collaborationId == collaborationId).first()    
    return agentCollaboration

def getCollaborationContribution(contributionId,collaborationId):
    contribution = session.query(cls.Contribution).filter(cls.Contribution.id == contributionId).filter(cls.Contribution.agentCollaborationId == cls.AgentCollaboration.id).filter(cls.AgentCollaboration.collaborationId == collaborationId).first()    
    return contribution




def deleteContribution(contribution):
    for contributionValue in contribution.contributionValues:
            session.delete(contributionValue)
    for contributor in contribution.contributors:
            session.delete(contributor)
    for evaluation in contribution.evaluations:
            session.delete(evaluation)
    session.delete(contribution)
    
def deleteAgentCollaboration(agentCollaboration):
    contributions = session.query(cls.Contribution).filter(cls.Contribution.agentCollaborationId == agentCollaboration.id).all()
    for contribution in contributions :
        deleteContribution(contribution)
    session.delete(agentCollaboration)

def deleteCollaboration(collaboration):
    agentCollaborations = session.query(cls.AgentCollaboration).filter(cls.AgentCollaboration.collaborationId == collaboration.id).all()
    for agentCollaboration in agentCollaborations:
        deleteAgentCollaboration(agentCollaboration)
    handles = collaboration.handles
    for handle in handles :
        session.delete(handle)
    session.delete(collaboration)

def deleteNetwork(network):  
    agentNetworks = network.agentNetworks  
    for agentNetwork in agentNetworks :
        session.delete(agentNetwork)
    collaborations = network.collaborations
    for collaboration in collaborations :
        deleteCollaboration(collaboration)
    session.delete(network)
        
def deleteAgent(agent):
    networks = session.query(cls.Network).filter(cls.Network.agentId == agent.id).all()
    for network in networks :
        deleteNetwork(network)
    agentHandles = session.query(cls.AgentHandle).filter(cls.AgentHandle.agentId == agent.id).all()
    for agentHandle in agentHandles :
        deleteAgentHandle(agentHandle)
    
    session.delete(agent)
    
def deleteHandle(handle):
    agentHandles = session.query(cls.AgentHandle).filter(cls.AgentHandle.handleId == handle.id).all()
    for agentHandle in agentHandles :
        deleteAgentHandle(agentHandle)
    session.delete(handle)
    
def deleteAgentHandle(agentHandle):
    networks = session.query(cls.Network).filter(cls.Network.agentHandleId == agentHandle.id).all()
    for network in networks :
        deleteNetwork(network)
    collaborations = session.query(cls.Collaboration).filter(cls.Collaboration.agentHandleId == agentHandle.id).all()
    for collaboration in collaborations :
        deleteCollaboration(collaboration)
    session.delete(agentHandle)
    
    
def getContributionDetail(contribution):
    for contributor in contribution.contributors:
            contributor.name= getAgentHandle(contributor.contributorId).agent.name
            contributor.id = contributor.contributorId
            
    last_evaluation = None 
    currentValuation = 0  
    evaluations = contribution.evaluations
    evaluations.sort(key=lambda x: x.timeCreated, reverse=False)    
    for evaluation in evaluations:
        last_evaluation = evaluation
        
    if (last_evaluation):
        currentValuation = last_evaluation.contributionValueAfterEvaluation
    contribution.tokenName = contribution.agentCollaboration.collaboration.tokenName
    contribution.currentValuation = currentValuation
    contribution.tokenSymbol = contribution.agentCollaboration.collaboration.tokenSymbol
    return contribution

def fillAgentDetails(agentHandle):
    agentHandle.name = agentHandle.agent.name
    agentHandle.fullName = agentHandle.agent.fullName
    agentHandle.imgUrl = agentHandle.agent.imgUrl
    return agentHandle