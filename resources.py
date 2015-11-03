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


agent_fields = {
    'id': fields.Integer,
}

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

network_fields = {
    'id': fields.Integer,
    'name': fields.String, 
    'description': fields.String,
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
    

    @marshal_with(agent_fields)
    def post(self):
        name = request.args.get('name')
        if(name == '' or name == None ):
            abort(404, message="name is required")
        handleName = request.args.get('handleName')
        handleType = request.args.get('handleType')
        if handleName == None :
            handleName = name
        if handleType == None :
            handleType = 'Backfeed'
        agentHandle = getAgentByNameAndType(name,handleName,handleType)
        if agentHandle :
            abort(404, message="Agent {} with handleName {} and handleType {} already exist".format(name,handleName,handleType))
        agent = getAgentByName(name) 
        if not agent :
            jsonStr = {
                    "name":name
                    }
            agent = cls.Agent(jsonStr,session)
            session.add(agent)
            session.flush()
        
        agentHandle = cls.AgentHandle()
        agentHandle.agentId = agent.id
        agentHandle.handleType = handleType
        agentHandle.handleName = handleName
        session.add(agentHandle)
        session.commit()
        return agentHandle, 201
        
    
    
class AgentParameterResource(Resource):
    @marshal_with(agent_handle_fields)
    def get(self, id):
        agentHandle = getAgentHandle(id)
        if not agentHandle:
            abort(404, message="Agent {} doesn't exist".format(id)) 
        agentHandle = fillAgentDetails(agentHandle)
        return agentHandle 
    
    
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
        
        
        
    
    @marshal_with(agent_fields)
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
    
    @marshal_with(network_fields)
    def get(self):
        networks = session.query(cls.Network).all()
        return networks
    
    def delete(self):
        networks = session.query(cls.Network).all()
        for network in networks :
            deleteNetwork(network)
        session.commit()
        return "Networks deleted successfully", 200
    
    @marshal_with(network_fields)
    def post(self):
        name = request.args.get('name')
        description = request.args.get('description')        
        agentHandleId = request.args.get('creator')
        
        if name == '' or name == None:
            abort(404, message="name is required")
        if agentHandleId == '' or agentHandleId == None:
            abort(404, message="creator is required")
        else :
            agentHandle = getAgentHandle(agentHandleId)
            if not agentHandle :
                abort(404, message="agentId {} does not exists".format(agentHandleId))
        
            
        network = session.query(cls.Network).filter(cls.Network.name == name).first()
        if network:
            abort(404, message="Network for name {} already exist".format(name))
        
        jsonStr = {"name":name,
                    "description":description,"agentHandleId":agentHandleId}
        network = cls.Network(jsonStr,session)
        session.add(network)
        session.commit()
        return network, 201
    
class NetworkParameterResource(Resource):
    
    @marshal_with(network_fields)
    def get(self, id):
        network = session.query(cls.Network).filter(cls.Network.id == id).first()
        if not network :
            abort(404, message="Network {} does not exists".format(id))
        return network
    
    def delete(self, id):
        network = session.query(cls.Network).filter(cls.Network.id == id).first()
        if network :
            deleteNetwork(network)           
            session.commit()
        return "Network deleted successfully", 200

    
class CollaborationResource(Resource):
    
    @marshal_with(collaboration_fields)
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
        
        return collaborations
    
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
    
    @marshal_with(collaboration_fields)
    def post(self):
        tokenName = request.args.get('tokenName')
        name = request.args.get('name')
        description = request.args.get('description')
        tokenSymbol = request.args.get('tokenSymbol')
        agentHandleId = request.args.get('creator')
        tokenTotal = request.args.get('tokenTotal')
        networkId = request.args.get('networkId')
        comment = request.args.get('comment')
        handles = request.args.get('handles')
        protocol = request.args.get('protocol')
        handlesJSON = {}
        contributorsJSON = {}
        if handles != '' and handles != None :
            handlesJSON = json.loads(handles)
        contributors = request.args.get('contributors')
        print 'contributors'+contributors
        if contributors != '' and contributors != None :
            contributorsJSON = json.loads(contributors)
        similarEvaluationRate = request.args.get('similarEvaluationRate')
        passingResponsibilityRate = request.args.get('passingResponsibilityRate')
        if protocol == '' or  protocol == None :
            abort(404, message="Protocol is required")
        if name == '' or name == None:
            abort(404, message="collaborationName is required")
        if networkId != '' and networkId != None:
            network = session.query(cls.Network).filter(cls.Network.id == networkId).first()
            if not network :
                abort(404, message="Network {} does not exists".format(networkId))
        if agentHandleId == '' or agentHandleId == None:
            abort(404, message="creator is required")
        else :
            agentHandle = getAgentHandle(agentHandleId)
            if not agentHandle :
                abort(404, message="agent{} does not exists".format(agentHandleId))
        if similarEvaluationRate == '' or similarEvaluationRate == None :
            similarEvaluationRate = 50 
        if passingResponsibilityRate == '' or passingResponsibilityRate == None:
            passingResponsibilityRate = 50 
            
        collaboration = session.query(cls.Collaboration).filter(cls.Collaboration.name == name).first()
        if collaboration:
            abort(404, message="Collaboration for name {} already exist".format(name))
        
        jsonStr = {"tokenName":tokenName,
                    "similarEvaluationRate":similarEvaluationRate,"passingResponsibilityRate":passingResponsibilityRate,"tokenTotal":tokenTotal,"protocol":protocol,
                    "tokenSymbol":tokenSymbol,"description":description,"networkId":networkId,"comment":comment,"name":name,"agentHandleId":agentHandleId}
        collaboration = cls.Collaboration(jsonStr,session)
        session.add(collaboration)
        session.flush()   
        creatorAlreadyCreated = False
        #create agent collaborations objects
        for contributor in contributorsJSON :
            agentCollaboration = cls.AgentCollaboration()
            agentCollaboration.collaborationId = collaboration.id
            contributorId = contributor['id']
            if int(agentHandleId) == int(contributorId):
                creatorAlreadyCreated = True;
            agentCollaboration.agentHandleId = contributorId
            agentCollaboration.tokens = float(int(tokenTotal)*int(contributor['percentage']))/100
            agentCollaboration.reputation = float(int(tokenTotal)*int(contributor['percentage']))/100
            session.add(agentCollaboration)
            
            agentNetwork = getAgentNetwork(contributorId, networkId)
            if not agentNetwork:
                agentNetwork = cls.AgentNetwork()
                agentNetwork.agentHandleId = contributorId
                agentNetwork.networkId = networkId
                session.add(agentNetwork)
            
        
        if creatorAlreadyCreated == False :
            agentCollaboration = cls.AgentCollaboration()
            agentCollaboration.collaborationId = collaboration.id
            agentCollaboration.agentHandleId = agentHandleId
            agentCollaboration.tokens = 0
            agentCollaboration.reputation = 0
            session.add(agentCollaboration)
            agentNetwork = getAgentNetwork(agentHandleId, networkId)
            if not agentNetwork:
                agentNetwork = cls.AgentNetwork()
                agentNetwork.agentHandleId = agentHandleId
                agentNetwork.networkId = networkId
                session.add(agentNetwork)
            
        for handle in handlesJSON :
            collaborationHandle = cls.CollaborationHandle()
            collaborationHandle.collaborationId = collaboration.id
            collaborationHandle.handleName = handle['handleName']
            collaborationHandle.handleType = handle['handleType']
            session.add(collaborationHandle)
            
        session.commit()    
        return collaboration, 201
    
class CollaborationParameterResource(Resource):
    
    @marshal_with(collaboration_fields)
    def get(self, id):
        collaboration = session.query(cls.Collaboration).filter(cls.Collaboration.id == id).first()
        if not collaboration :
            abort(404, message="collaborationId {} does not exists".format(id))
        return collaboration
    
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
    @marshal_with(contribution_fields)
    def get(self):
        collaborationId = request.args.get('collaborationId')
        key = request.args.get('key')
        contains = request.args.get('contains')
        if collaborationId != '' and  collaborationId != None  :
            collaboration = session.query(cls.Collaboration).filter(cls.Collaboration.id == collaborationId).first()
            if not collaboration :
                abort(404, message="Collaboration {} does not exists".format(collaborationId))
            contributions = []
            agentCollaborations = collaboration.agentCollaborations
            for agentCollaboration in agentCollaborations :
                contributions.extend(agentCollaboration.contributions)
        elif key != '' and  key != None and contains != '' and  contains != None :
            allContributions = session.query(cls.Contribution).all()
            contributions = []
            for contribution in allContributions:
                content = contribution.content
                handlesContent = json.loads(content)['content']
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
        
        for contribution in contributions :
            contribution = getContributionDetail(contribution)
        return contributions

    def delete(self):
        contributions = session.query(cls.Contribution).all()
        for contribution in contributions :
            deleteContribution(contribution)
        session.commit()
        return "Contributions deleted successfully", 200
    
    @marshal_with(contribution_fields)   
    def post(self): 
        collaborationId = request.args.get('collaborationId')
        agentHandleId = request.args.get('agentId')
        comment = request.args.get('comment')
        type = request.args.get('type')
        content = request.data
        agentHandle = None
        if type == '' or type == None :
            abort(404, message="Type is required")
            
        if agentHandleId == '' or agentHandleId == None :
            abort(404, message="Agent is required")
        else :
            agentHandle = getAgentHandle(agentHandleId)
            if not agentHandle :
                abort(404, message="agent {} does not exists".format(agentHandleId))
        
        if collaborationId == '' or collaborationId == None  :
            abort(404, message="Collaboration is required")
        else :
            collaboration = session.query(cls.Collaboration).filter(cls.Collaboration.id == collaborationId).first()
            if not collaboration :
                abort(404, message="Collaboration {} does not exists".format(collaborationId))
        agentCollaboration = session.query(cls.AgentCollaboration).filter(cls.AgentCollaboration.agentHandleId == agentHandleId).filter(cls.AgentCollaboration.collaborationId == collaborationId).first()
        if not agentCollaboration :
            abort(404, message="Agent {} does not exists in Collaboration {} ".format(agentHandleId,collaborationId))    
        contribution = cls.Contribution()
        contribution.agentHandleId = agentHandleId
        contribution.agentCollaborationId = agentCollaboration.id
        contribution.comment = comment
        contribution.content = content
        contribution.type = type
        session.add(contribution) 
        session.flush()  
        
        #adding default contributor
        
        contributionContributor = cls.ContributionContributor()
        contributionContributor.contributorId = agentHandleId
        contributionContributor.percentage = '100'
        contributionContributor.name = agentHandle.agent.name
        contribution.contributors.append(contributionContributor)
               
        #adding reputation stats for this contribution
        agentCollaborations = session.query(cls.AgentCollaboration).filter(cls.AgentCollaboration.collaborationId == collaborationId).all()
        for agentCollaboration in agentCollaborations :
              contributionValue = cls.ContributionValue()
              contributionValue.agentHandleId = agentCollaboration.agentHandleId
              contributionValue.agentCollaborationId = agentCollaboration.id
              contributionValue.contributionId = contribution.id
              contributionValue.reputationGain = 0
              contributionValue.reputation = agentCollaboration.reputation
              session.add(contributionValue)
        session.commit()    
        
        return contribution, 201
    
class ContributionParameterResource(Resource):
    @marshal_with(contribution_fields)
    def get(self, id):
        contribution = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        if not contribution:
            abort(404, message="Contribution {} doesn't exist".format(id))
        contribution = getContributionDetail(contribution)
        return contribution

    def delete(self, id):
        contribution = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        if not contribution:
            abort(404, message="Contribution {} doesn't exist".format(id))
        deleteContribution(contribution)
        session.commit()
        return "Contribution deleted successfully", 200
    

class EvaluationResource(Resource):
    @marshal_with(evaluation_fields)
    def get(self):
        contributionId = request.args.get('contributionId')
        evaluations = []
        if contributionId != '' and contributionId != None:
            contribution = session.query(cls.Contribution).filter(cls.Contribution.id == contributionId).first()
            if not contribution :
                abort(404, message="contributionId {} does not exists".format(contributionId))
            evaluations = contribution.evaluations
        evaluations = session.query(cls.Evaluation).all()
        return evaluations

    def delete(self):
        evaluations = session.query(cls.Evaluation).all()
        for evaluation in evaluations :
            session.delete(evaluation)
        session.commit()
        return "Evaluations deleted successfully", 200


    @marshal_with(evaluation_fields)
    def post(self):
        tokens = request.args.get('tokens')
        contributionId = request.args.get('contributionId')
        agentHandleId = request.args.get('agentId')
        stake = request.args.get('stake')
        agentHandle = None
        contribution = None
        if stake == '' or stake == None:
            abort(404, message="Stake is required")
        if tokens == '' or tokens == None:
            abort(404, message="Tokens is required")
            
        if agentHandleId == '' or agentHandleId == None:
            abort(404, message="Agent is required")
        else :
            agentHandle = getAgentHandle(agentHandleId)
            if not agentHandle :
                abort(404, message="agentId {} does not exists".format(agentHandleId))
        
        if contributionId == '' or contributionId == None:
            abort(404, message="Contribution is required")
        else :
            contribution = session.query(cls.Contribution).filter(cls.Contribution.id == contributionId).first()
            if not contribution :
                abort(404, message="contributionId {} does not exists".format(contributionId))
                
        
        if contribution.status != 'Open':
            abort(404, message="Contribution {} is not Open".format(contributionId))
        contributionValues = session.query(cls.ContributionValue).filter(cls.ContributionValue.contributionId == contribution.id).filter(cls.ContributionValue.agentCollaborationId == cls.AgentCollaboration.id).filter(cls.AgentCollaboration.agentHandleId == agentHandleId).filter(cls.AgentCollaboration.collaborationId == contribution.agentCollaboration.collaborationId).first()
        
        jsonStr = {"tokens":tokens,
                   "reputation":contributionValues.reputation,
                   "agentHandleId":agentHandleId,
                   "contributionId":contributionId,
                   "stake":stake, 
                   "timeCreated":datetime.now()
                    }

        evaluation = cls.Evaluation(jsonStr,session) 
        vd = ValueDistributer('ProtocolFunctionV1')
        vd.process_evaluation(evaluation,session)
        if(vd.error_occured):
            print vd.error_code
            # ToDo :  pass correct error message to agent
            abort(404, message="Failed to process evaluation {} due to"+vd.error_code.format(contributionId))

        return evaluation, 201
    
class EvaluationParameterResource(Resource):
    @marshal_with(evaluation_fields)
    def get(self, id):
        evaluation = session.query(cls.Evaluation).filter(cls.Evaluation.id == id).first()
        if not evaluation:
            abort(404, message="EvaluationId {} doesn't exist".format(id))
        return evaluation

    def delete(self, id):
        evaluation = session.query(cls.Evaluation).filter(cls.Evaluation.id == id).first()
        if not evaluation:
            abort(404, message="EvaluationId {} doesn't exist".format(id))
        session.delete(evaluation)
        session.commit()
        return "Evaluation deleted successfully", 200


    
    
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
    
def getAgent(id):
    agent = session.query(cls.Agent).filter(cls.Agent.id == id).first()    
    return agent



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

def getAgentByIdAndType(id,handleName,handleType):
    agentHandle = session.query(cls.AgentHandle).filter(cls.Agent.id == id).filter(cls.AgentHandle.agentId == cls.Agent.id).filter(cls.AgentHandle.handleName == handleName).filter(cls.AgentHandle.handleType == handleType).first()    
    return agentHandle

def getAgentNetwork(agentHandleId,networkId):
    agentNetwork = session.query(cls.AgentNetwork).filter(cls.AgentNetwork.agentHandleId == agentHandleId).filter(cls.AgentNetwork.networkId == networkId).first()    
    return agentNetwork


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