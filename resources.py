from db import session
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

userParser = reqparse.RequestParser()
userOrganizationParser = reqparse.RequestParser()
contributionParser = reqparse.RequestParser()
bidParser = reqparse.RequestParser()
closeContributionParser = reqparse.RequestParser()

contributionParser.add_argument('contributers', type=cls.Contributer, action='append')
contributionParser.add_argument('owner', type=int,required=True)
contributionParser.add_argument('users_organizations_id', type=int,required=True)
contributionParser.add_argument('min_reputation_to_close', type=str)
contributionParser.add_argument('file', type=str,required=True)
contributionParser.add_argument('title', type=str)

userParser.add_argument('userId', type=str)
userParser.add_argument('name', type=str,required=True)
userParser.add_argument('slack_id', type=str)


bidParser.add_argument('stake', type=str,required=True)
bidParser.add_argument('tokens', type=str,required=True)
bidParser.add_argument('reputation', type=str,required=True)    
bidParser.add_argument('contribution_id', type=str,required=True)
bidParser.add_argument('owner', type=int,required=True)

closeContributionParser.add_argument('owner', type=int,required=True)
closeContributionParser.add_argument('id', type=int,required=True)

user_fields = {
    'id': fields.Integer,
    'name': fields.String,    
}

user_org_fields = {
    'id': fields.Integer,
    'name': fields.String, 
    'tokens': fields.String,  
    'reputation': fields.String, 
     'url' : fields.String,
     'real_name':fields.String,
}

org_fields = {
    'id': fields.Integer,
    'name': fields.String, 
    'token_name': fields.String,
    'channelName': fields.String,      
}

userOrganization_fields = {
    'id': fields.Integer,
    'user_id': fields.String,
    'organization_id': fields.String,
    'org_tokens': fields.String,
    'org_reputation': fields.String,
    'channelId':fields.String
}

bid_fields = {
    'id': fields.Integer,
    'contribution_id': fields.Integer
}

bid_nested_fields = {}
bid_nested_fields['stake'] = fields.String
bid_nested_fields['tokens'] = fields.String
bid_nested_fields['reputation'] = fields.String
bid_nested_fields['owner'] = fields.Integer
bid_nested_fields['bidderName'] = fields.String

bid_status_nested_fields = {}
bid_status_nested_fields['time_created'] = fields.String
bid_status_nested_fields['tokens'] = fields.String
bid_status_nested_fields['reputation'] = fields.String
bid_status_nested_fields['contribution_value_after_bid'] = fields.Float
bid_status_nested_fields['stake'] = fields.Float
bid_status_nested_fields['owner'] = fields.Integer

contributer_nested_fields = {}
contributer_nested_fields['contributer_id'] = fields.String
contributer_nested_fields['contributer_percentage'] = fields.String
contributer_nested_fields['name'] = fields.String
contributer_nested_fields['real_name'] = fields.String
contributer_nested_fields['url'] = fields.String
contributer_nested_fields['project_reputation'] = fields.String

contribution_fields = {}
contribution_fields['id'] = fields.Integer
contribution_fields['time_created'] = fields.DateTime
contribution_fields['users_organizations_id'] = fields.Integer
contribution_fields['status'] = fields.String
contribution_fields['owner'] = fields.String
contribution_fields['file'] = fields.String
contribution_fields['title'] = fields.String
contribution_fields['tokenName'] = fields.String
contribution_fields['code'] = fields.String
contribution_fields['channelId'] = fields.String
contribution_fields['currentValuation'] = fields.Integer
contribution_fields['bids'] = fields.Nested(bid_nested_fields)
contribution_fields['contributionContributers'] = fields.Nested(contributer_nested_fields)

contribution_status_fields ={}
contribution_status_fields['currentValuation'] = fields.Integer
contribution_status_fields['reputationDelta'] = fields.Integer
contribution_status_fields['myValuation'] = fields.Integer
contribution_status_fields['myWeight'] = fields.Float
contribution_status_fields['groupWeight'] = fields.Float
contribution_status_fields['project_reputation'] = fields.Float
contribution_status_fields['totalSystemReputation'] = fields.Float
contribution_status_fields['file'] = fields.String
contribution_status_fields['title'] = fields.String
contribution_status_fields['bids'] = fields.Nested(bid_status_nested_fields)
contribution_status_fields['contributionContributers'] = fields.Nested(contributer_nested_fields)

contribution_status_nested_fields ={}
contribution_status_nested_fields['currentValuation'] = fields.Integer
contribution_status_nested_fields['reputationDelta'] = fields.Integer
contribution_status_nested_fields['id'] = fields.Integer
contribution_status_nested_fields['myWeight'] = fields.Float
contribution_status_nested_fields['title'] = fields.String
contribution_status_nested_fields['cTime'] = fields.String
contribution_status_nested_fields['tokenName'] = fields.String
contribution_status_nested_fields['owner'] = fields.String


member_status_fields ={}
member_status_fields['project_tokens'] = fields.String
member_status_fields['project_reputation'] = fields.String
member_status_fields['contributionLength'] = fields.String
member_status_fields['url'] = fields.String
member_status_fields['fullName'] = fields.String
member_status_fields['name'] = fields.String
member_status_fields['reputationPercentage'] = fields.String
member_status_fields['contributions'] = fields.Nested(contribution_status_nested_fields)


def getUser(id):
    user = session.query(cls.User).filter(cls.User.id == id).first()    
    return user
   
class UserResource(Resource):
    @marshal_with(user_org_fields)
    def get(self, id,orgId):
        char = getUser(id)
        userOrgObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == orgId).filter(cls.UserOrganization.user_id == id).first()
        print 'got Get for User fbid:'+id
        if not char:
            abort(404, message="User {} doesn't exist".format(id))       
        return {"id": char.id,"name":char.name,"tokens": userOrgObj.org_tokens,"reputation": userOrgObj.org_reputation} 
    
    def delete(self, id):
        char = getUser(id)
        if not char:
            abort(404, message="User {} doesn't exist".format(id))
        session.delete(char)
        session.commit()
        return {}, 204

    @marshal_with(user_fields)
    def put(self, id):
        parsed_args = userParser.parse_args()
        char = getUser(id)
        session.add(char)
        session.commit()
        return char, 201

    @marshal_with(user_fields)
    def post(self):
        parsed_args = userParser.parse_args()

        jsonStr = {
                    "name":parsed_args['name']
                    }
        user = cls.User(jsonStr,session)

        session.add(user)
        session.commit()
        return user, 201
    
class AllOrganizationResource(Resource):
    @marshal_with(org_fields)
    def get(self):
        organizations = session.query(cls.Organization).all()
        return organizations
    
class AllUserResource(Resource):
    @marshal_with(user_org_fields)
    def get(self,organizationId):
        users =[]    
        userOrganizationObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == organizationId).all()
        for userOrganization in userOrganizationObjects :
            print 'url is'+str(userOrganization.user.url)
            users.append({'url':userOrganization.user.url,'real_name':userOrganization.user.real_name,'id':userOrganization.user.id,'name':userOrganization.user.name,"tokens": userOrganization.org_tokens,"reputation": userOrganization.org_reputation})           
        return users
        
class BidResource(Resource):
    @marshal_with(bid_fields)
    def get(self, id):
        char = session.query(cls.Bid).filter(cls.Bid.id == id).first()
        print 'got Get for Bid fbid:'+id
        if not char:
            abort(404, message="Bid {} doesn't exist".format(id))
        return char

    def delete(self, id):
        char = session.query(cls.Bid).filter(cls.Bid.id == id).first()
        if not char:
            abort(404, message="Bid {} doesn't exist".format(id))
        session.delete(char)
        session.commit()
        return {}, 204

    @marshal_with(bid_fields)
    def put(self, id):
        parsed_args = bidParser.parse_args()
        char = session.query(cls.Bid).filter(cls.Bid.id == id).first()
        session.add(char)
        session.commit()
        return char, 201

    @marshal_with(bid_fields)
    def post(self):
        parsed_args = bidParser.parse_args()
        contributionid = parsed_args['contribution_id']        
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == contributionid).first()
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(contributionid))
        if contributionObject.status != 'Open':
            abort(404, message="Contribution {} is not Open".format(contributionid))
        userObj = getUser(parsed_args['owner'])        
        if not userObj:
            abort(404, message="User {} who is creating bid  doesn't exist".format(parsed_args['owner']))     
        jsonStr = {"tokens":parsed_args['tokens'],
                   "reputation":parsed_args['reputation'],
                   "owner":parsed_args['owner'],
                   "contribution_id":parsed_args['contribution_id'],
                   "stake":parsed_args['stake'], 
                   "time_created":datetime.now()
                    }

        bid = cls.Bid(jsonStr,session) 
        vd = ValueDistributer()
        vd.process_bid(bid,session)
        if(vd.error_occured):
            print vd.error_code
            # ToDo :  pass correct error message to user
            abort(404, message="Failed to process bid".format(contributionid))

        return bid, 201
    
class BidContributionResource(Resource):
    def get(self, contributionId,userId):
        char = session.query(cls.Bid).filter(cls.Bid.contribution_id == contributionId).filter(cls.Bid.owner == userId).first()   
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == contributionId).first()     
        if not char:
            return {"bidExists":"false","organizationId":contributionObject.userOrganization.organization_id}
        else:
            return {"bidExists":"true"}        

class ContributionResource(Resource):
    @marshal_with(contribution_fields)
    def get(self, id):
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        print 'got Get for Contribution fbid:'+id
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(id))
        for contributer in contributionObject.contributionContributers:
            contributer.name= getUser(contributer.contributer_id).name
        last_bid = None 
        currentValuation = 0      
        for bid in contributionObject.bids:
            bid.bidderName = getUser(bid.owner).name
            last_bid = bid
            
        if (last_bid):
            currentValuation = last_bid.contribution_value_after_bid
        contributionObject.tokenName = contributionObject.userOrganization.organization.token_name
        contributionObject.currentValuation = currentValuation
        contributionObject.code = contributionObject.userOrganization.organization.code

        return contributionObject

    def delete(self, id):
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(id))
        for contributer in contributionObject.contributionContributers:
            session.delete(contributer)
        for bid in contributionObject.bids:
            session.delete(bid)
        session.delete(contributionObject)
        session.commit()
        return {}, 204
    
    @marshal_with(contribution_fields)   
    def post(self):        
        parsed_args = contributionParser.parse_args()  
        contribution = cls.Contribution()
        contribution.owner = parsed_args['owner']
        contribution.min_reputation_to_close = parsed_args['min_reputation_to_close']
        contribution.file = parsed_args['file']
        contribution.owner = parsed_args['owner']
        contribution.title = parsed_args['title']
        contribution.users_organizations_id = parsed_args['users_organizations_id']
        userOrgObjectForOwner = session.query(cls.UserOrganization).filter(cls.UserOrganization.id == parsed_args['users_organizations_id']).first()
        userObj = getUser(contribution.owner) 
               
        if not userObj:
            abort(404, message="User who is creating contribution {} doesn't exist".format(contribution.owner))    
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.users_organizations_id == parsed_args['users_organizations_id']).first()
        firstContribution = False
        if (not contributionObject ):
            firstContribution = True
        for contributer in parsed_args['contributers']:             
            contributionContributer = cls.ContributionContributer()
            contributionContributer.contributer_id = contributer.obj1['contributer_id']
            if contributionContributer.contributer_id == '':
                continue
            userObj = getUser(contributionContributer.contributer_id)        
            if not userObj:
                abort(404, message="Contributer {} doesn't exist".format(contributionContributer.contributer_id))
            contributionContributer.contribution_id=contribution.id
            contributionContributer.name = userObj.name          
            contributionContributer.contributer_percentage=contributer.obj1['contributer_percentage']
            #if (firstContribution == True):
                 #userOrgObject = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == userOrgObjectForOwner.organization_id).filter(cls.UserOrganization.user_id == userObj.id).first()
                 #if userOrgObject:
                    #userOrgObject.org_reputation = contributer.obj1['contributer_percentage']
                    #session.add(userOrgObject)                                               
            contribution.contributionContributers.append(contributionContributer)  
        if(len(contribution.contributionContributers) == 0):
            contributionContributer = cls.ContributionContributer()
            contributionContributer.contributer_id = contribution.owner
            contributionContributer.contributer_percentage = '100'
            contributionContributer.name = userObj.name
            contribution.contributionContributers.append(contributionContributer)  
            #if (firstContribution == True):
                #userOrgObjectForOwner.org_reputation = 100
                #session.add(userOrgObjectForOwner) 
                                
        #if((parsed_args['intialBid'].obj1['tokens'] != '') & (parsed_args['intialBid'].obj1['reputation'] != '')):      
                #jsonStr = {"tokens":parsed_args['intialBid'].obj1['tokens'],
                   #"reputation":parsed_args['intialBid'].obj1['reputation'],
                   #"owner":contribution.owner,
                   #"contribution_id":contribution.id
                    #}
                #intialBidObj = cls.Bid(jsonStr,session)        
                #contribution.bids.append(intialBidObj)
        
        
        
        session.add(contribution)
        session.commit()        
        contribution.channelId = userOrgObjectForOwner.organization.channelId
        return contribution, 201


class CloseContributionResource(Resource):
    @marshal_with(contribution_fields)   
    def post(self):      
        parsed_args = closeContributionParser.parse_args()   
        ownerId = parsed_args['owner'] 
        contributionId = parsed_args['id'] 
        userObj = getUser(ownerId)  
        if not userObj:
            abort(404, message="User who is closing contribution {} doesn't exist".format(ownerId)) 
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == contributionId).first()
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(contributionId))
        if contributionObject.status != 'Open':
            abort(404, message="Contribution {} is already closed".format(contributionId))        
        if userObj.id != contributionObject.owner:
            abort(404, message="Only contribution owner can close this contribution".format(ownerId)) 
        
        # process contribution:
        if( not self.process_contribution(contributionObject) ):
            abort(404, message="Failed to process contribution".format(contributionId))

        # success: close contribution and commit DB session:
        contributionObject.status='Closed'
        session.add(contributionObject)
        session.commit()        
       
        return contributionObject, 201


    def process_contribution(self,contribution):
        print 'process_contribution contribution bids:\n'+str(contribution.bids)
        
        return True


class AllContributionResource(Resource):
    @marshal_with(contribution_fields)
    def get(self,organizationId):
        if organizationId == 'notintialized':
            organizationId = g.orgId
        contributionObject = session.query(cls.Contribution).filter(cls.UserOrganization.organization_id == organizationId).filter(cls.Contribution.users_organizations_id ==cls.UserOrganization.id).all()
        return contributionObject
    
class ContributionStatusResource(Resource):
    @marshal_with(contribution_status_fields)
    def get(self,id,userId):
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        print 'got Get for Contribution fbid:'+id
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(id))
        userOrgObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == userId).filter(cls.UserOrganization.organization_id == contributionObject.userOrganization.organization_id).first()
        userOrgObjs = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == contributionObject.userOrganization.organization_id).all()
        totalSystemReputation = 0
        for userOrgObjVar in userOrgObjs :
            totalSystemReputation = totalSystemReputation + userOrgObjVar.org_reputation
        contributionObject.totalSystemReputation = totalSystemReputation
        currentValuation = 0
        myValuation = 0
        myWeight = 0
        groupWeight = 0
        reputationDelta = 0
        last_bid = None
        for contributer in contributionObject.contributionContributers:
            contributer.name= getUser(contributer.contributer_id).name
            contributer.url= getUser(contributer.contributer_id).url
            contributer.real_name= getUser(contributer.contributer_id).real_name
            contributerUserOrgObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == contributer.contributer_id).filter(cls.UserOrganization.organization_id == contributionObject.userOrganization.organization_id).first()
            contributer.project_reputation = contributerUserOrgObj.org_reputation
        for bid in contributionObject.bids:
            last_bid = bid
            groupWeight = groupWeight + bid.weight
            if(str(bid.owner) == str(userId)):
                myWeight = bid.weight 
                reputationDelta = userOrgObj.org_reputation - bid.reputation
                myValuation = bid.tokens
        if (last_bid):
            currentValuation = last_bid.contribution_value_after_bid
        contributionObject.currentValuation = currentValuation
        contributionObject.reputationDelta = reputationDelta
        contributionObject.myValuation = myValuation
        contributionObject.myWeight = myWeight
        contributionObject.groupWeight = groupWeight
        contributionObject.project_reputation = userOrgObj.org_reputation
        return contributionObject
    
class MemberStatusAllOrgsResource(Resource):
    @marshal_with(member_status_fields)
    def get(self,slackTeamId,userId):        
        userOrgObjs = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == cls.User.id).filter(cls.User.slackId == userId).filter(cls.UserOrganization.organization_id == cls.Organization.id).filter(cls.Organization.slack_teamid == slackTeamId).all()
        userOrgObj = userOrgObjs[0]
        allContributions = session.query(cls.Contribution).all()
        currentValuation = 0
        myWeight = 0
        reputationDelta = 0
        userOrgObj.name = userOrgObj.user.name
        userOrgObj.fullName = userOrgObj.user.real_name
        userOrgObj.url = userOrgObj.user.url72
        countOfContribution = 0  
        userOrgObj.reputationPercentage = 'N/A'
        
        last_bid = None
        for contribution in allContributions:
            contributedCounted = False
            if(str(contribution.owner) == str(userOrgObj.user.id)):
                countOfContribution = countOfContribution + 1
                contributedCounted = True
            if contributedCounted == False:
                for contributionContributer in contribution.contributionContributers :
                    if(str(contributionContributer.contributer_id) == str(userOrgObj.user.id)):
                        countOfContribution = countOfContribution + 1
                        contributedCounted = True
            if contributedCounted == True:
                last_bid = None
                currentValuation = 0
                myWeight = 0
                reputationDelta = 0
                for bid in contribution.bids:
                    last_bid = bid
                    if(str(bid.owner) == str(userOrgObj.user.id)):
                        myWeight = bid.weight 
                        reputationDelta = userOrgObj.org_reputation - bid.reputation
                if (last_bid):
                    currentValuation = last_bid.contribution_value_after_bid
                contribution.currentValuation = currentValuation
                contribution.reputationDelta = reputationDelta
                contribution.myWeight = myWeight
                contribution.tokenName= contribution.userOrganization.organization.token_name
                contribution.cTime = contribution.time_created.date()
                if userOrgObj.id != contribution.userOrganization.id :
                    userOrgObj.contributions.append(contribution)
        userOrgObj.contributionLength = countOfContribution
        userOrgObj.org_tokens = 'N/A'
        userOrgObj.org_reputation = 'N/A'
        return userOrgObj    


class MemberStatusResource(Resource):
    @marshal_with(member_status_fields)
    def get(self,orgId,userId):        
        userOrgObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == cls.User.id).filter(cls.User.slackId == userId).filter(cls.UserOrganization.organization_id == orgId).first()
        userOrgObjs = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == orgId).all()
        allContributions = session.query(cls.Contribution).filter(cls.UserOrganization.id == cls.Contribution.users_organizations_id).filter(cls.UserOrganization.organization_id == orgId).all()
        totalReputation = 0;
        for userOrgObjVar in userOrgObjs:
            totalReputation = totalReputation + userOrgObjVar.org_reputation
        currentValuation = 0
        myWeight = 0
        reputationDelta = 0
        userOrgObj.name = userOrgObj.user.name
        userOrgObj.fullName = userOrgObj.user.real_name
        userOrgObj.url = userOrgObj.user.url72
        
        userOrgObj.reputationPercentage = (userOrgObj.org_reputation / totalReputation)*100
        userOrgObj.project_tokens = userOrgObj.org_tokens
        userOrgObj.project_reputation = userOrgObj.org_reputation
        last_bid = None
        countOfContribution = 0       
        for contribution in allContributions:
            contributedCounted = False
            if(str(contribution.owner) == str(userOrgObj.user.id)):
                countOfContribution = countOfContribution + 1
                contributedCounted = True
            if contributedCounted == False:
                for contributionContributer in contribution.contributionContributers :
                    if(str(contributionContributer.contributer_id) == str(userOrgObj.user.id)):
                        countOfContribution = countOfContribution + 1
                        contributedCounted = True
            if contributedCounted == True:
                last_bid = None
                currentValuation = 0
                myWeight = 0
                reputationDelta = 0
                for bid in contribution.bids:
                    last_bid = bid
                    if(str(bid.owner) == str(userOrgObj.user.id)):
                        myWeight = bid.weight 
                        reputationDelta = userOrgObj.org_reputation - bid.reputation
                if (last_bid):
                    currentValuation = last_bid.contribution_value_after_bid
                contribution.currentValuation = currentValuation
                contribution.reputationDelta = reputationDelta
                contribution.myWeight = myWeight
                contribution.cTime = contribution.time_created.date()
                contribution.tokenName= contribution.userOrganization.organization.token_name
                if(str(contribution.owner) != str(userOrgObj.user.id)):
                    userOrgObj.contributions.append(contribution)
        userOrgObj.contributionLength = countOfContribution
        for contribution in userOrgObj.contributions:
            print 'contribution.myWeight'+str(contribution.myWeight)
        return userOrgObj
    
    
class OrganizationTokenExistsResource(Resource):
    def get(self,tokenName):
        orgObj = session.query(cls.Organization).filter(cls.Organization.token_name == tokenName).first()
        if not orgObj:
            return {"tokenAlreadyExist":"false"}
        else:
             return {"tokenAlreadyExist":"true"}
         
class ChannelOrganizationExistsResource(Resource):
    def get(self,channelId,slackTeamId,userId):
        orgObj = session.query(cls.Organization).filter(cls.Organization.slack_teamid == slackTeamId).filter(cls.Organization.channelId == channelId).first()
        if not orgObj:
            return {"channleOrgExists":"false"}
        else:
            userOrgObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == userId).filter(cls.UserOrganization.organization_id == orgObj.id).first()
            return {"channleOrgExists":"true","userOrgId":userOrgObj.id,"orgId":orgObj.id}    
         
class OrganizationCodeExistsResource(Resource):
    def get(self,code):
        orgObj = session.query(cls.Organization).filter(cls.Organization.code == code).first()
        if not orgObj:
            return {"codeAlreadyExist":"false"}
        else:
             return {"codeAlreadyExist":"true"} 
         
class MemberOranizationsResource(Resource):
    @marshal_with(org_fields)
    def get(self,slackTeamId):
        orgObjs = session.query(cls.Organization).filter(cls.Organization.slack_teamid == slackTeamId).all()
        return  orgObjs
              
    
class OrganizationResource(Resource):
    
    @marshal_with(userOrganization_fields)
    def post(self):
        json = request.json
        orgObj = session.query(cls.Organization).filter(cls.Organization.code == json['code']).first()
        if orgObj:
            return {"codeExist":"true"}
        
        orgObj = session.query(cls.Organization).filter(cls.Organization.token_name == json['token_name']).first()
        if orgObj:
            return {"tokenExist":"true"}
        
        
        #channelId = createChannel(json['channelName'])
        jsonStr = {"token_name":json['token_name'],
                    "slack_teamid":json['slack_teamid'],"a":json['a'],"b":json['b'],
                    "name":json['name'],"code":json['code'],"channelName":json['channelName'],"channelId":json['channelId']}
        userOrgObj = cls.UserOrganization(jsonStr,session)        
        organization = cls.Organization(jsonStr,session)
        session.add(organization)
        session.flush()            
        createUserAndUserOrganizations(organization.id,json['contributers'],json['token'],json['b'])
        session.commit()        
        orgs = session.query(cls.Organization).filter(cls.Organization.slack_teamid == organization.slack_teamid).all()
        orgChannelId = ''
        count = 1
        for org in orgs:
            if count == 1:
                orgChannelId = org.channelId
            else:
                orgChannelId = orgChannelId + ','+ org.channelId
            count = count + 1;
        userOrgObj.channelId = orgChannelId

        return userOrgObj, 201
    
    def delete(self, id):
        orgObj = session.query(cls.Organization).filter(cls.Organization.id == id).first()
        if orgObj :
            userOrganizationObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == id).all()
            for userOrganization in userOrganizationObjects :
                contributionObjects = session.query(cls.Contribution).filter(cls.Contribution.users_organizations_id == userOrganization.id).all()
                for contributionObject in contributionObjects:                    
                    for contributer in contributionObject.contributionContributers:
                        session.delete(contributer)
                    for bid in contributionObject.bids:
                        session.delete(bid)
                    session.delete(contributionObject)
                session.delete(userOrganization)        
            session.delete(orgObj)
            session.commit()
        return {}, 204
    
def getSlackUsers():
    team_users_api_url = 'https://slack.com/api/users.list'
    headers = {'User-Agent': 'DEAP'}
    r = requests.get(team_users_api_url, params={'token':g.access_token}, headers=headers)
    users = json.loads(r.text)['members']
    print 'slack users:'+str(users)
    return users

    
class getAllSlackUsersResource(Resource):
    def get(self):
        users = getSlackUsers()
        usersJson = []
        for user in users :
            if user['deleted'] == True :
                continue
            if user['is_bot'] == True :
                continue
            jsonStr = {"id":user['id'],"name":user['name'],"url":user['profile']['image_48'],"real_name":user['profile']['real_name']}
            usersJson.append(jsonStr)
        return usersJson
    
def createChannel(channelName):
        team_users_api_url = 'https://slack.com/api/channels.create'
        headers = {'User-Agent': 'DEAP'}
        r = requests.post(team_users_api_url, params={'token':g.access_token,'name':channelName}, headers=headers)
        channelObj = json.loads(r.text)
        print str(channelObj)
        
        channelId = ''
        errorText = ''
        try:
            errorText = channelObj['error']
        except KeyError:
            errorText = ''   
        if errorText == '' :
            try:
                channelId = channelObj['channel']['id']
            except KeyError:
                channelId = ''
        else :
            channelId = 'name_taken'
        
        print 'channelId is'+channelId
        return channelId 
        
        
    
def createUserAndUserOrganizations(organizaionId,contributers,token,b):
    
    usersInSystem = session.query(cls.User).all()
    contributionDic = {}
    for contributer in contributers :
        contributionDic[contributer['contributer_id']] = (float(token)/100)*float(contributer['contributer_percentage'])
    usersDic = {}
    currentUser = '';
    for u in usersInSystem:
        if u.id == g.user_id:
            currentUser = u
        usersDic[u.name] = u.id
    # parse response:
    users = getSlackUsers()
    print 'slack users:'+str(users)
    for user in users :
        token = 0
        repuation = 0
        try:
            token = contributionDic[user['id']]
            repuation = (int(token))*10/pow(10,(int(b)/50)) 
        except KeyError:
            token = 0
            repuation = 0
        userId = ''
        if user['deleted'] == True :
            continue
        if user['is_bot'] == True :
            continue
        try:
            userId = usersDic[user['name']]
        except KeyError:
            userId = ''
        if userId  == g.user_id :
            currentUser.url = user['profile']['image_48']
            currentUser.url72 = user['profile']['image_72']
            currentUser.real_name = user['profile']['real_name']
            currentUser.slackId = user['id']
            session.add(currentUser)
        if userId == '':            
            jsonStr = {"name":user['name'],"slackId":user['id'],"url":user['profile']['image_48'],"url72":user['profile']['image_72'],"real_name":user['profile']['real_name']}
            u = cls.User(jsonStr,session)
            session.add(u) 
            session.flush() 
            userId = u.id
                         
        jsonStr = {"user_id":userId,
                    "organization_id":organizaionId,
                    "org_tokens":token,
                    "org_reputation":repuation
                    }
        userOrganization = cls.UserOrganization(jsonStr,session)
        session.add(userOrganization)    
    
  
    
def allContributionsFromUser(): 
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
    contribitions = [];
    user = session.query(cls.User).filter(cls.User.name == profile['user']).first()
    if not user:
        return []    
    bidsList = session.query(cls.Bid).filter(cls.Bid.owner == user.id).all()
    if not bidsList:
        return []
    for bid in bidsList:
        contribitions.append(bid.contribution_id)
    return contribitions