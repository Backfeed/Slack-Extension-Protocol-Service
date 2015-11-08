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

agent_group_fields = {
    'id': fields.Integer,
}



network_fields = {
    'id': fields.Integer,
    'name': fields.String, 
    'tokenName': fields.String,
    'tokenSymbol': fields.String,
    'status': fields.String,
    'similarEvaluationRate': fields.Integer,
    'passingResponsibilityRate': fields.Integer,        
}

agent_network_fields = {
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
contribution_fields['agentNetworkId'] = fields.Integer
contribution_fields['status'] = fields.String
contribution_fields['tokenSymbol'] = fields.String
contribution_fields['tokenName'] = fields.String
contribution_fields['currentValuation'] = fields.Integer
contribution_fields['evaluations'] = fields.Nested(evaluation_nested_fields)
contribution_fields['contributors'] = fields.Nested(contributor_nested_fields)

tag_fields = {}
tag_fields['name'] = fields.String
tag_fields['id'] = fields.Integer
tag_fields['linksCount'] = fields.Integer
tag_fields['popularity'] = fields.Integer

link_fields = {}
link_fields['name'] = fields.String
link_fields['title'] = fields.String
link_fields['url'] = fields.String
link_fields['id'] = fields.Integer
link_fields['rank'] = fields.Integer
link_fields['tags'] = fields.Nested(tag_fields)

result_fields = {}
result_fields['name'] = fields.String
result_fields['title'] = fields.String
result_fields['url'] = fields.String
result_fields['id'] = fields.Integer
result_fields['rank'] = fields.Integer
result_fields['resultType'] = fields.String
result_fields['linksCount'] = fields.Integer
result_fields['popularity'] = fields.Integer


    
class AgentResource(FlaskResource):
    @marshal_with(agent_handle_fields)
    def get(self):
        groupId = request.args.get('groupId')
        agents = []
        if(groupId != None ) :
            agentGroups = session.query(cls.AgentGroup).filter(cls.AgentGroup.groupId == groupId).all() 
            
            for agentGroup in agentGroups :
                jsonStr = {
                    "id":agentGroup.agent.id,
                    "name":agentGroup.agent.name,
                    "imgUrl":agentGroup.agent.imgUrl
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
        groupId = request.args.get('groupId')
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
        elif(groupId != None ) :
            agentGroup = session.query(cls.AgentGroup).filter(cls.AgentGroup.groupId == groupId).filter(cls.AgentGroup.agentHandleId == id).first() 
            if agentGroup :
                session.delete(agentGroup)
            session.commit()
            return "Agent Groups deleted successfully", 200
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
    
class AgentFindByGroup(Resource):
    @marshal_with(agent_handle_fields)
    def get(self):
        groupId = request.args.get('groupId')
        if(groupId != None ) :
            group = session.query(cls.Group).filter(cls.Group.id == groupId).first()
            if not group :
                abort(404, message="Group {} does not exists".format(groupId))
            agentGroups = group.agentGroups
            agentHandlesList = []
            for agentGroup in agentGroups:
                agentHandle = agentGroup.agentHandle
                agentHandle = fillAgentDetails(agentHandle)
                agentHandlesList.append(agentHandle)
        return agentHandlesList
    
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
    
class AgentUpdateGroup(Resource):
    @marshal_with(agent_group_fields)
    def put(self,id):
        groupId = request.args.get('groupId')
        if(groupId == '' or groupId == None ):
            abort(404, message="groupId is required")
        group = session.query(cls.Group).filter(cls.Group.id == groupId).first()
        if not group :
            abort(404, message="Group {} does not exists".format(groupId))
        agentHandle = getAgentHandle(id)
        if not agentHandle :
            abort(404, message="agentHandle {} does not exists".format(id))
        agentGroup = getAgentGroup(id, groupId)
        if agentGroup :
            abort(404, message="agentGroup already exist with agent {} and group {}".format(id,groupId))
        agentGroup = cls.AgentGroup()
        agentGroup.agentHandleId = id
        agentGroup.groupId = groupId
        session.add(agentGroup)
        session.commit()
        return agentGroup
        
    
    

class GroupResource(Resource):
    
    def get(self):
        groups = session.query(cls.Group).all()
        fields = request.args.get('fields')
        groupsToShow = []
        for group in groups :
            groupsToShow.append(groupString(group,fields))
        return groupsToShow
        
    
    def post(self):
        postData = request.data
        description = ''
        groupProtocol = ''
        agent = None
        memberGroups = []
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
                groupProtocol = postDataJSON['groupProtocol']
            except KeyError :
                abort(404, message="protocol is required")
                
            try :
                agents = postDataJSON['agents']
                for agentId in agents:
                    memberGroup = getAgent(agentId)
                    if not memberGroup :
                        abort(404, message="member agent does not exists".format(agentId))
                    memberGroups.append(memberGroup)
            except KeyError :
                memberGroups = []
        
        group = cls.Group()
        group.name = name
        group.description = description
        group.agentId = agent.id
        if groupProtocol == '' or groupProtocol == None:
            abort(404, message="protocol is required")
        group.protocol = json.dumps(groupProtocol)
        
        session.add(group)
        session.flush()
        
        for memberGroup in memberGroups :
            agentGroup = cls.AgentGroup()
            agentGroup.agentId = memberGroup.id
            agentGroup.groupId = group.id
            session.add(agentGroup)
            
        session.commit()
        return {"id":group.id}, 201
    
class GroupParameterResource(Resource):
    
    def get(self, id):
        group = session.query(cls.Group).filter(cls.Group.id == id).first()
        if not group :
            abort(404, message="Group {} does not exists".format(id))
        fields = request.args.get('fields')
        groupsToShow = groupString(group,fields)
        return groupsToShow
    
    @marshal_with(agent_group_fields)
    def put(self,id):
        if(id == '' or id == None ):
            abort(404, message="groupId is required")
        group = session.query(cls.Group).filter(cls.Group.id == id).first()
        if not group :
            abort(404, message="Group {} does not exists".format(id))
        postData = request.data
        if postData != '' and postData != None :
            postDataJSON = json.loads(postData)
            agent = getAgent(postDataJSON['agentId'])
            if not agent :
                abort(404, message="agent {} does not exists".format(postDataJSON['agentId']))
            agentGroup = getAgentGroup(postDataJSON['agentId'], id)
            if agentGroup :
                abort(404, message="agentGroup already exist with agent {} and group {}".format(postDataJSON['agentId'],id))
            agentGroup = cls.AgentGroup()
            agentGroup.agentId = postDataJSON['agentId']
            agentGroup.groupId = id
            session.add(agentGroup)
            session.commit()
        return agentGroup
    
    

    
class NetworkResource(Resource):
    
    def get(self):
        groupId = request.args.get('groupId')
        agentId = request.args.get('agentId')
        if(groupId != None and agentId == None) :
            group = session.query(cls.Group).filter(cls.Group.id == groupId).first()
            if not group :
                abort(404, message="Group {} does not exists".format(groupId))
            networks = group.networks
        
        elif(groupId != None and agentId != None) :
            group = session.query(cls.Group).filter(cls.Group.id == groupId).first()
            if not group :
                abort(404, message="Group {} does not exists".format(groupId))
            allnetworks = group.networks
            networks = []
            for network in allnetworks :
                agentNetworks = network.agentNetworks
                for agentNetwork in agentNetworks :
                    if int(agentNetwork.agentHandleId) == int(agentId) :
                        networks.append(network)
                        break
                        
        else :
            networks = session.query(cls.Network).all()       
        fields = request.args.get('fields')
        networksToShow = []
        for network in networks :
            networksToShow.append(networkString(network,fields))
        return networksToShow
    
    def delete(self):
        groupId = request.args.get('groupId')
        if(groupId != None ) :
            group = session.query(cls.Group).filter(cls.Group.id == groupId).first()
            if not group :
                abort(404, message="Group {} does not exists".format(groupId))
            networks = group.networks
        else :
            networks = session.query(cls.Network).all()
            
        for network in networks :
            deleteNetwork(network)
        session.commit()
        return "Networks deleted successfully", 200
    
    
    def post(self):
        postData = request.data
        description = ''
        group = None
        agent = None
        network = cls.Network()
        if postData != '' and postData != None :
            postDataJSON = json.loads(postData)
            try :
                agentId = postDataJSON['creator']
                agent = getAgent(agentId)
                if not agent :
                    abort(404, message="creator does not exists".format(agentId))
            except KeyError :
                abort(404, message="creator is required")
            network.agentId = agent.id
            try :
                groupId = postDataJSON['group']
                group = getGroup(groupId)
                if not group :
                    abort(404, message="group {} doesn't exist".format(groupId))
            except KeyError :
                abort(404, message="group is required")
            network.groupId = group.id 
                
            try :
                description = postDataJSON['description']
            except KeyError :
                abort(404, message="description is required")
            network.description = description
            
            try :
                name = postDataJSON['name']
            except KeyError :
                abort(404, message="name is required")
            network.name = name
            
            try :
                comment = postDataJSON['comment']
                network.comment = comment
            except KeyError :
                comment = ''
                
            
            try :
                token = postDataJSON['token']
                network.tokenName = token['name']
                network.tokenSymbol = token['symbol']
                network.tokenTotal = token['total']
            except KeyError :
                abort(404, message="Tokens is required")
                
            try :
                networkProtocol = postDataJSON['networkProtocol']
                if networkProtocol != '' or networkProtocol != None :
                    try:
                        type = networkProtocol['type']
                        parameters = networkProtocol['parameters']
                        network.protocol = json.dumps(networkProtocol)
                    except KeyError :
                        abort(404, message="networkProtocol type and parameters is required")
                    
                
            except KeyError :
                networkProtocol = ''
                
                
            session.add(network)
            session.flush()
                
            try :
                contributors = postDataJSON['contributors']
                for contributor in contributors:
                    agentGroup = getAgentGroup(contributor['id'], group.id)
                    if not agentGroup :
                        abort(404, message="contributor {} does not exists in group {}".format(contributor['id'],group.id))
                    agentNetwork = cls.AgentNetwork()
                    agentNetwork.networkId = network.id
                    agentNetwork.agentId = agentGroup.agent.id
                    agentNetwork.tokens = int(network.tokenTotal)*float(contributor['ownership'])
                    agentNetwork.reputation = int(network.tokenTotal)*float(contributor['ownership'])
                    session.add(agentNetwork)
                if len(contributors) == 0 :
                    agentNetwork = cls.AgentNetwork()
                    agentNetwork.networkId = network.id
                    agentNetwork.agentId = agent.id
                    agentNetwork.tokens = network.tokenTotal
                    agentNetwork.reputation = network.tokenTotal
                    session.add(agentNetwork)
            except KeyError :
                agentNetwork = cls.AgentNetwork()
                agentNetwork.networkId = network.id
                agentNetwork.agentId = agent.id
                agentNetwork.tokens = network.tokenTotal
                agentNetwork.reputation = network.tokenTotal
                session.add(agentNetwork)
                
            try :
                handles = postDataJSON['handles']
                for handle in handles:
                    networkHandle = cls.NetworkHandle()
                    networkHandle.networkId = network.id
                    networkHandle.handleName = handle['name']
                    networkHandle.handleType = handle['type']
                    session.add(networkHandle)
            except KeyError :
                handles = ''
        
            #submit founding contribution
            
        session.commit()    
        return {"id":network.id}, 201
    
class GetNetworksByGroupResource(Resource):
    
    def get(self, id):
        networks = session.query(cls.Network).filter(cls.Network.groupId == id).all()
        fields = request.args.get('fields')
        networksToShow = []
        for network in networks :
            networksToShow.append(networkString(network,fields))
        return networksToShow
    

class GetNetworksByAgentResource(Resource):
    
    def get(self, id):
        agent = getAgent(id)
        if not agent :
            abort(404, message="Agent {} does not exists".format(id))
        groupId = request.args.get('groupId')
        if groupId != None and groupId != '' :
            group = getGroup(groupId)
            if not group :
                abort(404, message="group {} does not exists".format(groupId))
            networks = session.query(cls.Network).filter(cls.Network.groupId == groupId).filter(cls.Network.agentId == id).all()
        else :
            networks = session.query(cls.Network).filter(cls.Network.agentId == id).all()
        fields = request.args.get('fields')
        networksToShow = []
        for network in networks :
            networksToShow.append(networkString(network,fields))
        return networksToShow
    
class GetContributionByAgentResource(Resource):
    
    def get(self, id):
        agent = getAgent(id)
        if not agent :
            abort(404, message="Agent {} does not exists".format(id))
        networkId = request.args.get('networkId')
        if networkId != None and networkId != '' :
            network = getNetwork(id)
            if not network :
                abort(404, message="networkId {} does not exists".format(networkId))
            contributions = session.query(cls.Contribution).filter(cls.Contribution.agentNetworkId == cls.AgentNetwork.id).filter(cls.AgentNetwork.agentId == id).filter(cls.AgentNetwork.networkId == network.id).all()
        else :
            contributions = session.query(cls.Contribution).filter(cls.Contribution.agentNetworkId == cls.AgentNetwork.id).filter(cls.AgentNetwork.agentId == id).all()
        fields = request.args.get('fields')
        contributionssToShow = []
        for contribution in contributions :
            contributionssToShow.append(contributionString(contribution,fields))
        return contributionssToShow
    
   
    
class GetContributionByNetworkResource(Resource):
    
    def get(self, id):
        network = getNetwork(id)
        if not network :
            abort(404, message="networkId {} does not exists".format(id))
        contributions = session.query(cls.Contribution).filter(cls.Contribution.agentNetworkId == cls.AgentNetwork.id).filter(cls.AgentNetwork.networkId == id).all()
        fields = request.args.get('fields')
        contributionssToShow = []
        for contribution in contributions :
            contributionssToShow.append(contributionString(contribution,fields))
        return contributionssToShow
    
    
class NetworkParameterResource(Resource):
    
    def get(self, id):
        network = getNetwork(id)
        if not network :
            abort(404, message="networkId {} does not exists".format(id))
        fields = request.args.get('fields')
        return networkString(network,fields)
    
    def delete(self, id):
        network = session.query(cls.Network).filter(cls.Network.id == id).first()
        if network :
            deleteNetwork(network)            
            session.commit()
        return "Network deleted successfully", 200
    
    
    
class NetworkClose(Resource):

    @marshal_with(contribution_fields)
    def put(self):
        networkId = request.args.get('id')
        network = session.query(cls.Network).filter(cls.Network.id == networkId).first()
        if not network :
            abort(404, message="networkId {} does not exists".format(networkId)) 
        contributions = network.contributions 
        winningContribution = None
        maxContributionValueAfterEvaluation = 0
        for contribution in contributions :
            if contribution.contributionValueAfterEvaluation > maxContributionValueAfterEvaluation :
                maxContributionValueAfterEvaluation = contribution.contributionValueAfterEvaluation
                winningContribution = contribution
            contribution.status = 'Closed'
            session.add(contribution) 
        network.status = 'Closed'
        session.add(network) 
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
        jsonString = {}
        type = None
        agent = None
        network = None
        agentNetwork = None
        postData = request.data
        
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
                networkId = postDataJSON['network']
                network = session.query(cls.Network).filter(cls.Network.id == networkId).first()
                if not network :
                    abort(404, message="Network {} does not exists".format(networkId))
                    
                agentNetwork = getAgentNetwork(agent.id,network.id)
                if not agentNetwork :
                    abort(404, message="Agent {} does not exists in Network {} ".format(agent.id,networkId)) 
                
            except KeyError :
                abort(404, message="network is required")
                
            try :
                comment = postDataJSON['comment']
                
            except KeyError :
                comment = ''
                
            try :
                type = postDataJSON['type']
                
            except KeyError :
                abort(404, message="Type is required")
                
            
                
            
            #adding reputation stats for this contribution
            agentNetworks = session.query(cls.AgentNetwork).filter(cls.AgentNetwork.networkId == network.id).all()
            
                  
            previousTokens = agentNetwork.tokens
                
            try :
                content = postDataJSON['content']
                if type == 'URLAndTags' or type == 'Tags':
                    linkName = content['url']
                    evaluation1 = None
                    if type != 'Tags':
                        evaluation1 = content['evaluation']
                        
                    tags = content['tags']
                    link = getLINK(linkName)
                    jsonString['ids'] = []
                    if not link :
                        if type == 'Tags':
                            abort(404, message="Link  does not exist")
                        link = cls.LINK()
                        link.name = linkName
                        contribution = createContribution(agent.id,agentNetwork.id,comment,type,postDataJSON,agentNetworks,json.dumps(content))
                        link.contributionId = contribution.id
                        session.add(link)    
                        session.flush()
                        evaluation = cls.Evaluation() 
                        evaluation.agentId = agent.id
                        evaluation.tokens = evaluation1
                        evaluation.stake = .5*agentNetwork.reputation/100
                        evaluation.reputation = agentNetwork.reputation
                        evaluation.contributionId = contribution.id 
                        session.add(evaluation)  
                        session.flush()
                        jsonString['ids'].append('contribution '+ str(contribution.id)+'for linkName '+linkName) 
                        jsonString['ids'].append('evaluation '+str(evaluation.id)+'for linkName '+linkName)  
                    else :
                        if type != 'Tags':
                            contributionId = link.contribution.id
                            evaluation = getEvaluation(contributionId, agent.id)
                            if evaluation :
                                jsonString['ids'].append('evaluation already for linkName ' +linkName )
                            else :
                                evaluation = cls.Evaluation() 
                                evaluation.agentId = agent.id
                                evaluation.tokens = evaluation1
                                evaluation.stake = .5*agentNetwork.reputation/100
                                evaluation.reputation = agentNetwork.reputation
                                evaluation.contributionId = contribution.id 
                                session.add(evaluation)  
                                session.flush()
                                jsonString['ids'].append('evaluation '+str(evaluation.id)+'for linkName '+linkName)
                    
                    for tagName in tags:
                        tag = getTag(tagName)
                        if not tag:
                            tag = cls.Tag()
                            tag.name = tagName
                            contribution = createContribution(agent.id,agentNetwork.id,comment,type,postDataJSON,agentNetworks,json.dumps(content))
                            tag.contributionId = contribution.id
                            session.add(tag)    
                            session.flush()
                            evaluation = cls.Evaluation() 
                            evaluation.agentId = agent.id
                            evaluation.tokens = 1
                            evaluation.stake = .1*agentNetwork.reputation/100
                            evaluation.reputation = agentNetwork.reputation
                            evaluation.contributionId = contribution.id 
                            session.add(evaluation)  
                            session.flush()
                            jsonString['ids'].append('contribution '+ str(contribution.id)+'for tagName '+tagName) 
                            jsonString['ids'].append('evaluation '+str(evaluation.id)+'for tagName '+tagName) 
                        else :
                            contributionId = tag.contribution.id
                            evaluation = getEvaluation(contributionId, agent.id)
                            if evaluation :
                                jsonString['ids'].append('evaluation already for tagName ' +tagName )
                            else :
                                evaluation = cls.Evaluation() 
                                evaluation.agentId = agent.id
                                evaluation.tokens = 1
                                evaluation.stake = .1*agentNetwork.reputation/100
                                evaluation.reputation = agentNetwork.reputation
                                evaluation.contributionId = contribution.id 
                                session.add(evaluation)  
                                session.flush()
                                jsonString['ids'].append('evaluation '+str(evaluation.id)+'for tagName '+tagName)
                        tagLink = getTaglink(tag.id, link.id)
                        if not tagLink :
                            tagLINK = cls.TagLINK()
                            tagLINK.tagId = tag.id
                            tagLINK.linkId = link.id
                            tagLINK.contributionId = contribution.id
                            session.add(tagLINK)    
                            session.flush()
                else :
                    contribution = createContribution(agent.id,agentNetwork.id,comment,type,postDataJSON,agentNetworks,json.dumps(content))            
                if type == 'milestone':
                    contributions = content['contributions']
                    for contribution in contributions:
                        if not getNetworkContribution(contribution.id, network.id) :
                            abort(404, message="contribution {} does not exist in network".format(contribution.id,network.id)) 
                    submitter = content['submitter']
                    submitterCoolaboration = session.query(cls.Network).filter(cls.Network.id == submitter).filter(cls.Network.groupId == network.groupId).first()
                    if submitterCoolaboration == None :
                        abort(404, message="submitterCoolaboration {} does not exist".format(submitter)) 
            except KeyError :
                abort(404, message="content is required") 
                
            
        session.commit()  
        agentNetwork = getAgentNetwork(agent.id,network.id) 
        newtokens = agentNetwork.tokens  
        jsonString['contributorsBalance'] = []
        jsonString['contributorsBalance'].append({'newTokenBalance':newtokens,'oldTokenBalance':previousTokens,'id':agent.id})
        return jsonString, 201
    
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
                contributionId = postDataJSON['contributionId']
                contribution = session.query(cls.Contribution).filter(cls.Contribution.id == contributionId).first()
                if not contribution :
                    abort(404, message="contributionId {} does not exists".format(id))
                evaluation.contributionId = contribution.id        
            except KeyError :
                abort(404, message="contribution is required")
            previousTokens = getAgentNetwork(agent.id, contribution.agentNetwork.networkId).tokens
            previousReputation = getAgentNetwork(agent.id, contribution.agentNetwork.networkId).reputation
            if contribution.type != 'URLAndTags' and contribution.type != 'Tags':        
                try :
                    stake = postDataJSON['stake']
                    evaluation.stake = stake
                except KeyError :
                    abort(404, message="stake is required") 
            else :
                if contribution.tag != None :
                    evaluation.stake = .5*previousReputation/100
                    evaluation.reputation = previousReputation
                else :
                    evaluation.stake = .1*previousReputation/100
                    evaluation.reputation = previousReputation
                
        
        if contribution.status != 'Open':
            abort(404, message="Contribution {} is not Open".format(id))
        contributionValues = session.query(cls.ContributionValue).filter(cls.ContributionValue.contributionId == contribution.id).filter(cls.ContributionValue.agentNetworkId == cls.AgentNetwork.id).filter(cls.AgentNetwork.agentId == agent.id).filter(cls.AgentNetwork.networkId == contribution.agentNetwork.networkId).first()
        evaluation.reputation = contributionValues.reputation
        existingEvaluation = getEvaluation(contribution.id, agent.id)
        if existingEvaluation :
            abort(404, message="Evaluation already exists")
        previousTokens = getAgentNetwork(agent.id, contribution.agentNetwork.networkId).tokens
        previousReputation = getAgentNetwork(agent.id, contribution.agentNetwork.networkId).reputation
        session.add(evaluation)
        session.commit()
        #vd = ValueDistributer('ProtocolFunctionV1')
        #vd.process_evaluation(evaluation,session)
        #if(vd.error_occured):
            #print vd.error_code
            # ToDo :  pass correct error message to agent
            #abort(404, message="Failed to process evaluation {} due to"+vd.error_code.format(contribution.id))
        fields = request.args.get('fields')
        currentTokens = getAgentNetwork(agent.id, contribution.agentNetwork.networkId).tokens
        currentReputation = getAgentNetwork(agent.id, contribution.agentNetwork.networkId).reputation
        jsonString = {}
        jsonString['id'] = evaluation.id
        jsonString['contributionNewValue'] = evaluation.contributionValueAfterEvaluation
        jsonString['senderTokenReputationChange'] = {'agentId':agentId,'agentNewReputationBalance':currentReputation,'agentOldReputationBalance':previousReputation,'agentNewTokenBalance':currentTokens,'agentOldTokenBalance':previousTokens}
        return jsonString, 201
    
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
        for tag in tags :
            tag.id = tag.contribution.id
            tag.linksCount = len(tag.links)
            tag.popularity = 12
        
        return tags
    
class LinkResource(Resource):
    
    @marshal_with(link_fields)
    def get(self,id):
        tagName = request.args.get('tag')
        if tagName == '' and tagName == None :
            abort(404, message="tagName is required")
        link = session.query(cls.LINK).filter(cls.LINK.id == id).first()
        if not link :
             abort(404, message="link {} does not exist".format(id))
        contribution = link.contribution
        contribution.name = link.name
        contribution.title = json.loads(contribution.content)['title']
        contribution.url = json.loads(contribution.content)['url']
        taglinks = link.tags 
        for taglink in taglinks:
            taglink.popularity = 12
            taglink.name = taglink.tag.name
            taglink.linksCount = len(taglink.tag.links)
            contribution.tags = []
            contribution.tags.append(taglink)
        return contribution

class GetLinksByTagResource(Resource):
    
    @marshal_with(link_fields)
    def get(self):
        tagName = request.args.get('tag')
        if tagName == '' and tagName == None :
            abort(404, message="tagName is required")
        tagLINKs = session.query(cls.TagLINK).filter(cls.TagLINK.tagId == cls.Tag.id).filter(cls.Tag.name == tagName).all()
        contributions = []
        for tagLINK in tagLINKs :
            link = tagLINK.link
            contribution = link.contribution
            contribution.title = json.loads(contribution.content)['title']
            contribution.url = json.loads(contribution.content)['url']
            tags = link.tags 
            for tag in tags:
                tag.popularity = 12
                tag.linksCount = len(tag.links)
                contribution.tags = []
                contribution.tags.append(tag)
            contributions.append(contribution)
        return contributions
    
class GetTagsByLinkResource(Resource):
    
    @marshal_with(tag_fields)
    def get(self):
        linkName = request.args.get('url')
        if linkName == '' and linkName == None :
            abort(404, message="url is required")
        link = session.query(cls.LINK).filter(cls.LINK.name == linkName).first()
        if not link :
            abort(404, message="link {} does not exists".format(linkName))
        taglinks = link.tags
        for taglink in taglinks :
            taglink.id = taglink.tag.id
            taglink.name = taglink.tag.name
            taglink.linksCount = len(taglink.tag.links)
            taglink.popularity = 12
        return taglinks
    
class GetLinksANDTagsResource(Resource):
    
    @marshal_with(result_fields)
    def get(self):
        query = request.args.get('query')
        if query == '' and query == None :
            abort(404, message="query is required")
        
        results = []
        links = session.query(cls.LINK).filter(cls.LINK.name.like('%'+query+'%')).all()
        for link in links :
            link.resultType = 'link'
            contribution = link.contribution
            link.title = json.loads(contribution.content)['title']
            link.url = json.loads(contribution.content)['url']
            link.rank = 1
            results.append(link)
        
        tags = session.query(cls.Tag).filter(cls.Tag.name.like('%'+query+'%')).all()
        for tag in tags :
            tag.resultType = 'tag'
            tag.linksCount = len(tag.links)
            tag.popularity = 12
            results.append(tag)
        
        return results
    

        
        
    
class NetworkStatsForContributionsResource(Resource):
    
    @marshal_with(contribution_fields)
    def get(self, id):
        network = session.query(cls.Network).filter(cls.Network.id == id).first()
        if not network :
            abort(404, message="networkId {} does not exists".format(id))
        networkContributions = session.query(cls.Contribution).filter(cls.Contribution.agentNetworkId == cls.AgentNetwork.id).filter(cls.Contribution.AgentNetwork.networkId == cls.Network.id).all()
        return networkContributions
    
class NetworkStatsForEvaluationsResource(Resource):
    
    @marshal_with(evaluation_fields)
    def get(self, id):
        network = session.query(cls.Network).filter(cls.Network.id == id).first()
        if not network :
            abort(404, message="networkId {} does not exists".format(id))
        networkEvaluations = session.query(cls.Evaluation).filter(cls.Evaluation.contributionId == cls.Contribution.id).filter(cls.Contribution.agentNetworkId == cls.AgentNetwork.id).filter(cls.Contribution.AgentNetwork.networkId == cls.Network.id).all()
        return networkEvaluations
    
class AgentStatsForContributionsResource(Resource):
    
    @marshal_with(contribution_fields)
    def get(self, id):
        agent = session.query(cls.Agent).filter(cls.Agent.id == id).first()
        if not agent :
            abort(404, message="agentId {} does not exists".format(id))
        agentContributions = session.query(cls.Contribution).filter(cls.Contribution.agentNetworkId == cls.AgentNetwork.id).filter(cls.Contribution.AgentNetwork.agentId == cls.Agent.id).all()
        return agentContributions
    
class AgentStatsForEvaluationsResource(Resource):
    
    @marshal_with(evaluation_fields)
    def get(self, id):
        agent = session.query(cls.Agent).filter(cls.Agent.id == id).first()
        if not agent :
            abort(404, message="agentId {} does not exists".format(id))
        agentEvaluations = session.query(cls.Evaluation).filter(cls.Evaluation.contributionId == cls.Contribution.id).filter(cls.Contribution.agentNetworkId == cls.AgentNetwork.id).filter(cls.Contribution.AgentNetwork.agentId == cls.Agent.id).all()
        return agentEvaluations
    

def agentString(agent,fields):
    data = {}
    try :
        if fields == '' or fields == None :
            data['name'] = agent.name
            data['id'] = agent.id
            data['handles'] = []
            data['groups'] = []
            data['networks'] = []
            data['contributions'] = []
            for handle in agent.agentHandles:
                dataHandles = handleString(handle,None)
                data['handles'].append(dataHandles)
            for agentGroup in agent.agentGroups:
                dataGroups = groupString(agentGroup.group,None)
                data['groups'].append(dataGroups)
            for agentNetwork in agent.agentNetworks:
                dataNetworks = networkString(agentNetwork.network,None)
                dataNetworks['tokens'] = agentNetwork.tokens
                dataNetworks['reputation'] = agentNetwork.reputation
                data['networks'].append(dataNetworks)
            for contribution in agent.agentContributions:
                dataContributions = contributionString(contribution,None)
                data['contributions'].append(dataContributions)        
        else :
            fieldSet = fields.split(',')
            for field in fieldSet :
                fieldSet1 = field.split('.',1)
                if fieldSet1[0] == 'groups' :
                    data['groups'] = []
                    if(len(fieldSet1) == 1) :
                        fieldSetForGroup = None
                    else :
                        fieldSetForGroup = fieldSet1[1]
                    for agentGroup in agent.agentGroups:
                        dataGroups = groupString(agentGroup.group,fieldSetForGroup)
                        data['groups'].append(dataGroups)
                        
                elif fieldSet1[0] == 'handles' :
                    data['handles'] = []
                    if(len(fieldSet1) == 1) :
                        fieldSetForHandle = None
                    else :
                        fieldSetForHandle = fieldSet1[1]
                    for handle in agent.agentHandles:
                        dataHandles = handleString(handle,fieldSetForHandle)
                        data['handles'].append(dataHandles) 
                        
                elif fieldSet1[0] == 'networks' :
                    data['networks'] = []
                    if(len(fieldSet1) == 1) :
                        fieldSetFoNetwork = None
                    else :
                        fieldSetFoNetwork = fieldSet1[1]
                    for agentNetwork in agent.agentNetworks:
                        dataNetworks = networkString(agentNetwork.network,fieldSetFoNetwork)
                        if fieldSetFoNetwork == 'tokens' :
                            dataNetworks['tokens'] = agentNetwork.tokens
                        if fieldSetFoNetwork == 'reputation' :
                            dataNetworks['reputation'] = agentNetwork.reputation
                        if fieldSetFoNetwork == None :
                            dataNetworks['tokens'] = agentNetwork.tokens
                            dataNetworks['reputation'] = agentNetwork.reputation
                        data['networks'].append(dataNetworks)
                        
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

def groupString(group,fields):
    try :
        data = {}
        if fields == '' or fields == None :
            data['id'] = group.id
            data['agentId'] = group.agentId
            data['name'] = group.name
            data['description'] = group.description
            data['protocol'] = json.loads(group.protocol)
        else :
            fieldSet = fields.split(',')
            for field in fieldSet :
                if field == 'protocol' :
                    data[field] = json.loads(group.protocol)
                elif field == 'networks' :
                    data[field] = []
                    for network in group.networks:
                        dataContributors = networkString(network,None)
                        data[field].append(dataContributors)
                elif 'networks' in field :
                    fields1 = field.split('.',1)
                    data['networks'] = []
                    for network in group.networks:
                        dataContributors = networkString(network,fields1[1])
                        data['contributors'].append(dataContributors)
                else :
                    data[field] = group.__dict__[field]
            
    except :
            print 'Could not get data from group.'  
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

def networkString(network,fields):
    try:
        data = {}
        if fields == '' or fields == None :
            data['id'] = network.id
            data['agentId'] = network.agentId
            data['groupId'] = network.groupId
            data['tokenName'] = network.tokenName
            data['name'] = network.name
            data['description'] = network.description
            data['tokenSymbol'] = network.tokenSymbol
            data['tokenTotal'] = network.tokenTotal
            data['comment'] = network.comment
            data['status'] = network.status
            data['protocol'] = json.loads(network.protocol)
            data['handles'] = []
            for handle in network.handles:
                datahandles = {}
                datahandles['handleName'] = handle.handleName
                datahandles['handleType'] = handle.handleType
                data['handles'].append(datahandles)
            data['contributors'] = []
            for contributor in network.agentNetworks:
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
                    data[field] = json.loads(network.protocol)
                elif field == 'handles' :
                    data[field] = []
                    for handle in network.handles:
                        datahandles = {}
                        datahandles['handleName'] = handle.handleName
                        datahandles['handleType'] = handle.handleType
                        data[field].append(datahandles)
                elif 'handles' in field :
                    fields1 = field.split('.')
                    data['handles'] = []
                    for handle in network.handles:
                        datahandles = {}
                        datahandles[fields1[1]] = handle.__dict__[fields1[1]]
                        data['handles'].append(datahandles)
                elif field == 'contributors' :
                    data[field] = []
                    for contributor in network.agentNetworks:
                        dataContributors = {}
                        dataContributors['id'] = contributor.id
                        dataContributors['agentId'] = contributor.agentId
                        dataContributors['tokens'] = contributor.tokens
                        dataContributors['reputation'] = contributor.reputation
                        data[field].append(dataContributors)
                elif 'contributors' in field :
                    fields1 = field.split('.')
                    data['contributors'] = []
                    for contributor in network.agentNetworks:
                        dataContributors = {}
                        dataContributors[fields1[1]] = contributor.__dict__[fields1[1]]
                        data['contributors'].append(dataContributors)
                else :
                    data[field] = network.__dict__[field]
    
    except :
            print 'Could not get data from network.' 
            
        
    return data

def contributionString(contribution,fields):
    try: 
        data = {}
        dataContributors = {}
        if fields == '' or fields == None :
            data['id'] = contribution.id
            data['agentId'] = contribution.agentId
            data['agentNetworkId'] = contribution.agentNetworkId
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
            
    

def getNetwork(id):
    network = session.query(cls.Network).filter(cls.Network.id == id).first()    
    return network

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

def getGroup(id):
    group = session.query(cls.Group).filter(cls.Group.id == id).first()    
    return group

def createContribution(agentId,agentNetworkId,comment,type,postDataJSON,agentNetworks,content):
    contribution = cls.Contribution()
    contribution.agentId = agentId
    contribution.agentNetworkId = agentNetworkId
    contribution.comment = comment
    contribution.type = type
    contribution.content = content
    session.add(contribution)
    session.flush()
    
    for agentNetwork in agentNetworks :
          contributionValue = cls.ContributionValue()
          contributionValue.agentId = agentNetwork.agentId
          contributionValue.agentNetworkId = agentNetwork.id
          contributionValue.contributionId = contribution.id
          contributionValue.reputationGain = 0
          contributionValue.reputation = agentNetwork.reputation
          session.add(contributionValue)
                  
                  
    try :
        contributors = postDataJSON['contributors']
        for contributor in contributors:
            agentNetwork = getAgentNetwork(contributor['id'], network.id)
            if not agentNetwork :
                abort(404, message="contributor {} does not exists in Network {}".format(contributor['id'],network.id))
            contributionContributor = cls.ContributionContributor()
            contributionContributor.contributorId = agentNetwork.agentId
            contributionContributor.percentage = float(contributor['ownership'])*100
            contributionContributor.contributionId = contribution.id
            session.add(contributionContributor)    
            
        if len(contributors) == 0 :
            contributionContributor = cls.ContributionContributor()
            contributionContributor.contributorId = agentId
            contributionContributor.percentage = 100
            contributionContributor.contributionId = contribution.id
            session.add(contributionContributor) 
    except KeyError :
            contributionContributor = cls.ContributionContributor()
            contributionContributor.contributorId = agentId
            contributionContributor.percentage = 100
            contributionContributor.contributionId = contribution.id
            session.add(contributionContributor)
    return contribution
                        
    



def getByAgentAndHandle(id,handleId):
    agentHandle = session.query(cls.AgentHandle).filter(cls.AgentHandle.agentId == id).filter(cls.AgentHandle.handleId == handleId).first()    
    return agentHandle

def getEvaluation(contributionId,agentId):
    evaluation = session.query(cls.Evaluation).filter(cls.Evaluation.agentId == agentId).filter(cls.Evaluation.contributionId == contributionId).first()    
    return evaluation

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

def getAgentGroup(agentId,groupId):
    agentGroup = session.query(cls.AgentGroup).filter(cls.AgentGroup.agentId == agentId).filter(cls.AgentGroup.groupId == groupId).first()    
    return agentGroup

def getAgentNetwork(agentId,networkId):
    agentNetwork = session.query(cls.AgentNetwork).filter(cls.AgentNetwork.agentId == agentId).filter(cls.AgentNetwork.networkId == networkId).first()    
    return agentNetwork

def getNetworkContribution(contributionId,networkId):
    contribution = session.query(cls.Contribution).filter(cls.Contribution.id == contributionId).filter(cls.Contribution.agentNetworkId == cls.AgentNetwork.id).filter(cls.AgentNetwork.networkId == networkId).first()    
    return contribution




def deleteContribution(contribution):
    for contributionValue in contribution.contributionValues:
            session.delete(contributionValue)
    for contributor in contribution.contributors:
            session.delete(contributor)
    for evaluation in contribution.evaluations:
            session.delete(evaluation)
    session.delete(contribution)
    
def deleteAgentNetwork(agentNetwork):
    contributions = session.query(cls.Contribution).filter(cls.Contribution.agentNetworkId == agentNetwork.id).all()
    for contribution in contributions :
        deleteContribution(contribution)
    session.delete(agentNetwork)

def deleteNetwork(network):
    agentNetworks = session.query(cls.AgentNetwork).filter(cls.AgentNetwork.networkId == network.id).all()
    for agentNetwork in agentNetworks:
        deleteAgentNetwork(agentNetwork)
    handles = network.handles
    for handle in handles :
        session.delete(handle)
    session.delete(network)

def deleteGroup(group):  
    agentGroups = group.agentGroups  
    for agentGroup in agentGroups :
        session.delete(agentGroup)
    networks = group.networks
    for network in networks :
        deleteNetwork(network)
    session.delete(group)
        
def deleteAgent(agent):
    groups = session.query(cls.Group).filter(cls.Group.agentId == agent.id).all()
    for group in groups :
        deleteGroup(group)
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
    groups = session.query(cls.Group).filter(cls.Group.agentHandleId == agentHandle.id).all()
    for group in groups :
        deleteGroup(group)
    networks = session.query(cls.Network).filter(cls.Network.agentHandleId == agentHandle.id).all()
    for network in networks :
        deleteNetwork(network)
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
    contribution.tokenName = contribution.agentNetwork.network.tokenName
    contribution.currentValuation = currentValuation
    contribution.tokenSymbol = contribution.agentNetwork.network.tokenSymbol
    return contribution

def fillAgentDetails(agentHandle):
    agentHandle.name = agentHandle.agent.name
    agentHandle.fullName = agentHandle.agent.fullName
    agentHandle.imgUrl = agentHandle.agent.imgUrl
    return agentHandle