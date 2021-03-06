from db import session
# -*- coding: utf-8 -*-
import classes as cls

from flask.ext.restful import reqparse
from flask.ext.restful import abort
from flask.ext.restful import fields
from flask.ext.restful import marshal_with
import json
from auth import login_required,parse_token
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
bidParser = reqparse.RequestParser()
milestonebidParser = reqparse.RequestParser()
closeContributionParser = reqparse.RequestParser()


userParser.add_argument('name', type=str,required=True)
userParser.add_argument('slack_id', type=str)
userParser.add_argument('twitterHandle', type=str)


bidParser.add_argument('evaluation', type=str,required=True)
bidParser.add_argument('contributionId', type=str,required=True)

milestonebidParser.add_argument('tokens', type=int,required=True)
milestonebidParser.add_argument('milestoneId', type=int,required=True)

closeContributionParser.add_argument('id', type=int,required=True)

user_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'displayName': fields.String,
    'imgUrl': fields.String,
}

user_org_fields = {
    'id': fields.Integer,
    'name': fields.String, 
    'tokens': fields.String,  
    'reputation': fields.String, 
     'imgUrl' : fields.String,
     'real_name':fields.String,
}

org_fields = {
    'orgId': fields.Integer,
    'id': fields.Integer,
    'name': fields.String, 
    'token_name': fields.String,
    'channelName': fields.String,
    'channelId': fields.String,       
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
bid_nested_fields['userId'] = fields.Integer
bid_nested_fields['bidderName'] = fields.String

bid_status_nested_fields = {}
bid_status_nested_fields['date'] = fields.String
bid_status_nested_fields['tokens'] = fields.String
bid_status_nested_fields['reputation'] = fields.String
bid_status_nested_fields['contributionValueAfterBid'] = fields.Float
bid_status_nested_fields['stake'] = fields.Float
bid_status_nested_fields['userId'] = fields.Integer

contributor_nested_fields = {}
contributor_nested_fields['id'] = fields.String
contributor_nested_fields['percentage'] = fields.String
contributor_nested_fields['name'] = fields.String
contributor_nested_fields['real_name'] = fields.String
contributor_nested_fields['imgUrl'] = fields.String
contributor_nested_fields['project_reputation'] = fields.String

contribution_fields = {}
contribution_fields['id'] = fields.Integer
contribution_fields['time_created'] = fields.DateTime
contribution_fields['users_organizations_id'] = fields.Integer
contribution_fields['status'] = fields.String
contribution_fields['userId'] = fields.String
contribution_fields['description'] = fields.String
contribution_fields['title'] = fields.String
contribution_fields['tokenName'] = fields.String
contribution_fields['code'] = fields.String
contribution_fields['channelId'] = fields.String
contribution_fields['currentValuation'] = fields.Integer
contribution_fields['bids'] = fields.Nested(bid_nested_fields)
contribution_fields['contributors'] = fields.Nested(contributor_nested_fields)

contribution_status_fields ={}
contribution_status_fields['id'] = fields.Integer
contribution_status_fields['time_created'] = fields.DateTime
contribution_status_fields['users_organizations_id'] = fields.Integer
contribution_status_fields['status'] = fields.String
contribution_status_fields['userId'] = fields.String
contribution_status_fields['currentValuation'] = fields.Float
contribution_status_fields['valueIndic'] = fields.Integer
contribution_status_fields['myReputationDelta'] = fields.Integer
contribution_status_fields['myEvaluation'] = fields.Integer
contribution_status_fields['myWeight'] = fields.Float
contribution_status_fields['groupWeight'] = fields.Float
contribution_status_fields['channelId'] = fields.String
contribution_status_fields['project_reputation'] = fields.Float
contribution_status_fields['totalSystemReputation'] = fields.Float
contribution_status_fields['description'] = fields.String
contribution_status_fields['title'] = fields.String
contribution_status_fields['tokenName'] = fields.String
contribution_status_fields['code'] = fields.String
contribution_status_fields['bids'] = fields.Nested(bid_status_nested_fields)
contribution_status_fields['contributors'] = fields.Nested(contributor_nested_fields)

contribution_status_nested_fields ={}
contribution_status_nested_fields['currentValuation'] = fields.Integer
contribution_status_nested_fields['reputationDelta'] = fields.Integer
contribution_status_nested_fields['id'] = fields.Integer
contribution_status_nested_fields['myWeight'] = fields.Float
contribution_status_nested_fields['title'] = fields.String
contribution_status_nested_fields['cTime'] = fields.String
contribution_status_nested_fields['tokenName'] = fields.String
contribution_status_nested_fields['userId'] = fields.String

project_nested_fields ={}
project_nested_fields['id'] = fields.Integer
project_nested_fields['channelName'] = fields.String
project_nested_fields['name'] = fields.String


member_status_fields ={}
member_status_fields['tokens'] = fields.String
member_status_fields['tokenName'] = fields.String
member_status_fields['code'] = fields.String
member_status_fields['reputation'] = fields.String
member_status_fields['contributionLength'] = fields.String
member_status_fields['imgUrl'] = fields.String
member_status_fields['fullName'] = fields.String
member_status_fields['name'] = fields.String
member_status_fields['reputationPercentage'] = fields.String
member_status_fields['contributions'] = fields.Nested(contribution_status_nested_fields)
member_status_fields['projects'] = fields.Nested(project_nested_fields)



milestoneContributor_nested_fields = {}
milestoneContributor_nested_fields['id'] = fields.String
milestoneContributor_nested_fields['percentage'] = fields.String
milestoneContributor_nested_fields['name'] = fields.String
milestoneContributor_nested_fields['real_name'] = fields.String
milestoneContributor_nested_fields['imgUrl'] = fields.String

contribution_contributor_nested_fields = {}
contribution_contributor_nested_fields['memberId'] = fields.String
contribution_contributor_nested_fields['imgUrl'] = fields.String

milestoneContribution_nested_fields = {}
milestoneContribution_nested_fields['title'] = fields.String
milestoneContribution_nested_fields['description'] = fields.String
milestoneContribution_nested_fields['date'] = fields.String
milestoneContribution_nested_fields['valuation'] = fields.String
milestoneContribution_nested_fields['contribution_id'] = fields.Integer
milestoneContribution_nested_fields['remainingContributors'] = fields.Integer
milestoneContribution_nested_fields['contributors'] = fields.Nested(contribution_contributor_nested_fields)



milestone_fields = {}
milestone_fields['id'] = fields.Integer
milestone_fields['current_org_id'] = fields.Integer
milestone_fields['contribution_id'] = fields.Integer
milestone_fields['start_date'] = fields.DateTime
milestone_fields['end_date'] = fields.DateTime
milestone_fields['users_organizations_id'] = fields.Integer
milestone_fields['userId'] = fields.String
milestone_fields['description'] = fields.String
milestone_fields['tokens'] = fields.Float
milestone_fields['totalValue'] = fields.Float
milestone_fields['title'] = fields.String
milestone_fields['tokenName'] = fields.String
milestone_fields['channelName'] = fields.String
milestone_fields['destChannelId'] = fields.String
milestone_fields['destChannelName'] = fields.String
milestone_fields['code'] = fields.String
milestone_fields['destination_org_id'] = fields.Integer
milestone_fields['contributors'] = fields.Nested(milestoneContributor_nested_fields)
milestone_fields['contributions'] = fields.Nested(milestoneContribution_nested_fields)



def getUser(id):
    user = session.query(cls.User).filter(cls.User.id == id).first()    
    return user

def getUserBySlackId(id):
    user = session.query(cls.User).filter(cls.User.slackId == id).first()    
    return user

def getUserByTwitterId(id):
    user = session.query(cls.User).filter(cls.User.twitterHandle == id).first()    
    return user

class UserSlackResource(Resource):
    @marshal_with(user_fields)
    def get(self, slackId):
        char = getUserBySlackId(slackId)
        if not char:
            abort(404, message="User {} doesn't exist".format(id))       
        return {"id": char.id,"name":char.name,"displayName": char.name,"imgUrl": char.imgUrl}
   
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
        json = request.json
        twitterHandle = json['twitterHandle']
        char = getUser(id)
        if twitterHandle != None :
            char.twitterHandle = twitterHandle
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
        payload = parse_token(request)
        slackTeamId = payload['slackTeamId']
        organizations = session.query(cls.Organization).filter(cls.Organization.slack_teamid == slackTeamId).all()
        for organization in organizations :
            organization.orgId = organization.id
        return organizations
    
class AllOrganizationForCurrentTeamResource(Resource):
    @marshal_with(org_fields)
    def get(self,slackTeamId):
        organizations = session.query(cls.Organization).filter(cls.Organization.slack_teamid == slackTeamId).all()
        return organizations
    
class AllUserResource(Resource):
    @marshal_with(user_org_fields)
    def get(self,organizationId):
        users =[]    
        userOrganizationObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == organizationId).all()
        for userOrganization in userOrganizationObjects :
            print 'imgUrlis'+str(userOrganization.user.imgUrl)
            users.append({'imgUrl':userOrganization.user.imgUrl,'real_name':userOrganization.user.real_name,'id':userOrganization.user.id,'name':userOrganization.user.name,"tokens": userOrganization.org_tokens,"reputation": userOrganization.org_reputation})           
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
        contributionid = parsed_args['contributionId']        
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == contributionid).first()
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(contributionid))
        if contributionObject.status != 'Open':
            abort(404, message="Contribution {} is not Open".format(contributionid))
        payload = parse_token(request)
        userId = payload['sub']
        slackTeamId = payload['slackTeamId']
        
            
        userObj = getUser(userId)        
        if not userObj:
            abort(404, message="User {} who is creating bid  doesn't exist".format(userId))
        contributionValues = session.query(cls.ContributionValue).filter(cls.ContributionValue.contribution_id == contributionObject.id).filter(cls.ContributionValue.users_organizations_id == cls.UserOrganization.id).filter(cls.UserOrganization.user_id == userObj.id).filter(cls.UserOrganization.organization_id == contributionObject.userOrganization.organization_id).first()
        stake = 0
        if slackTeamId == 'T02H16QH6' :
            stake = contributionValues.reputation*2/100
        else :
            stake = contributionValues.reputation*5/100
        jsonStr = {"tokens":parsed_args['evaluation'],
                   "reputation":contributionValues.reputation,
                   "userId":userId,
                   "contribution_id":contributionid,
                   "stake":stake, 
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
    
class MilestoneBidResource(Resource):
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
    def post(self):
        parsed_args = milestonebidParser.parse_args()
        milestoneId = parsed_args['milestoneId']        
        milestoneObject = session.query(cls.Milestone).filter(cls.Milestone.id == milestoneId).first()
        if not milestoneObject:
            abort(404, message="Milestone {} doesn't exist".format(milestoneId)) 
        contributionid = milestoneObject.contribution_id     
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == contributionid).first()
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(contributionid))
        if contributionObject.status != 'Open':
            abort(404, message="Contribution {} is not Open".format(contributionid))
        payload = parse_token(request)
        userId = payload['sub']
        slackTeamId = payload['slackTeamId']
        userObj = getUser(userId)        
        if not userObj:
            abort(404, message="User {} who is creating bid  doesn't exist".format(userId))
        contributionValues = session.query(cls.ContributionValue).filter(cls.ContributionValue.contribution_id == contributionObject.id).filter(cls.ContributionValue.users_organizations_id == cls.UserOrganization.id).filter(cls.UserOrganization.user_id == userObj.id).filter(cls.UserOrganization.organization_id == contributionObject.userOrganization.organization_id).first()
        stake = 0
        if slackTeamId == 'T02H16QH6' :
            stake = contributionValues.reputation*2/100
        else :
            stake = contributionValues.reputation*5/100
        jsonStr = {"tokens":parsed_args['tokens'],
                   "reputation":contributionValues.reputation,
                   "userId":userId,
                   "contribution_id":contributionid,
                   "stake":stake, 
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
        char = session.query(cls.Bid).filter(cls.Bid.contribution_id == contributionId).filter(cls.Bid.userId == userId).first()   
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == contributionId).first() 
        if contributionObject.status == 'Closed':
            return {"contributionClose":"true"}  
        if not char:
            return {"contributionClose":"false","bidExists":"false","organizationId":contributionObject.userOrganization.organization_id}
        else:
            return {"contributionClose":"false","bidExists":"true"} 
        
        
class MilestoneBidContributionResource(Resource):
    def get(self, milestoneId,userId):
        milestoneObj = session.query(cls.Milestone).filter(cls.Milestone.id == milestoneId).first()
        contributionId = milestoneObj.contribution_id
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == contributionId).first()
        char = session.query(cls.Bid).filter(cls.Bid.contribution_id == contributionId).filter(cls.Bid.userId == userId).first()
        if contributionObject.status == 'Closed':   
             return {"contributionClose":"true",'contributionId':contributionId} 
        if not char:
            return {"contributionClose":"false","bidExists":"false","organizationId":contributionObject.userOrganization.organization_id,'contributionId':contributionId}
        else:
            return {"contributionClose":"false","bidExists":"true",'contributionId':contributionId}       

class ContributionResource(Resource):
    @marshal_with(contribution_fields)
    def get(self, id):
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        print 'got Get for Contribution fbid:'+id
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(id))
        for contributor in contributionObject.contributors:
            contributor.name= getUser(contributor.contributor_id).name
            contributor.id = contributor.contributor_id
            
        last_bid = None 
        currentValuation = 0  
        bids = contributionObject.bids
        bids.sort(key=lambda x: x.time_created, reverse=False)    
        for bid in bids:
            bid.bidderName = getUser(bid.userId).name
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
        for contributor in contributionObject.contributors:
            session.delete(contributor)
        for bid in contributionObject.bids:
            session.delete(bid)
        session.delete(contributionObject)
        session.commit()
        return {}, 204
    
    @marshal_with(contribution_fields)   
    def post(self):        
        json = request.json
        contribution = cls.Contribution()
        contribution.min_reputation_to_close = 0
        contribution.description = json['description']
        contribution.title = json['title']
        session.add(contribution) 
        session.flush()  
        twitterHandle = None  
        userObj = None
        for contributor in json['contributors']:             
            contributionContributor = cls.ContributionContributor()
            try :
                twitterHandle = contributor['twitterHandle']
            except KeyError :
                twitterHandle = None
            if twitterHandle != None :
                userObj = getUserByTwitterId(twitterHandle)
            else :
                if contributor['id'] == '':
                    continue
                userObj = getUserBySlackId(contributor['id']) 
            if not userObj:
                abort(404, message="Contributor {} doesn't exist".format(contributionContributor.contributor_id))
            contributionContributor.contributor_id = userObj.id
            contributionContributor.contribution_id=contribution.id
            contributionContributor.name = userObj.name          
            contributionContributor.percentage=contributor['percentage']
            #if (firstContribution == True):
                 #userOrgObject = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == userOrgObjectForOwner.organization_id).filter(cls.UserOrganization.user_id == userObj.id).first()
                 #if userOrgObject:
                    #userOrgObject.org_reputation = contributor.obj1['contributor_percentage']
                    #session.add(userOrgObject)                                               
            contribution.contributors.append(contributionContributor)  
         
        if twitterHandle == None :
           payload = parse_token(request)
           contribution.userId = payload['sub']
        else :
            contribution.userId = userObj.id
            
        
        orgObject = session.query(cls.Organization).filter(cls.Organization.channelId == json['channelId']).first()
        userOrgObjectForOwner = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == orgObject.id).filter(cls.UserOrganization.user_id == contribution.userId).first()
        contribution.users_organizations_id = userOrgObjectForOwner.id
        session.add(contribution) 
        userObj = getUser(contribution.userId) 
             
        if not userObj:
            abort(404, message="User who is creating contribution {} doesn't exist".format(contribution.userId))    
        
        if(len(contribution.contributors) == 0):
            contributionContributor = cls.ContributionContributor()
            contributionContributor.contributor_id = contribution.userId
            contributionContributor.percentage = '100'
            contributionContributor.name = userObj.name
            contribution.contributors.append(contributionContributor)  
            #if (firstContribution == True):
                #userOrgObjectForOwner.org_reputation = 100
                #session.add(userOrgObjectForOwner) 
                                
        #if((parsed_args['intialBid'].obj1['tokens'] != '') & (parsed_args['intialBid'].obj1['reputation'] != '')):      
                #jsonStr = {"tokens":parsed_args['intialBid'].obj1['tokens'],
                   #"reputation":parsed_args['intialBid'].obj1['reputation'],
                   #"userId":contribution.userId,
                   #"contribution_id":contribution.id
                    #}
                #intialBidObj = cls.Bid(jsonStr,session)        
                #contribution.bids.append(intialBidObj)
        
        
        
        
        userOrgObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == userOrgObjectForOwner.organization_id).all()
        for userOrgObject in userOrgObjects :
              contributionValue = cls.ContributionValue()
              contributionValue.user_id = userOrgObject.user_id
              contributionValue.users_organizations_id = userOrgObject.id
              contributionValue.contribution_id = contribution.id
              contributionValue.reputationGain = 0
              contributionValue.reputation = userOrgObject.org_reputation
              contributionValue.user_id = userOrgObject.user_id
              session.add(contributionValue)
        
        session.commit()    
        for contributor in contribution.contributors:             
            contributor.id=contributor.contributor_id
        contribution.channelId = userOrgObjectForOwner.organization.channelId
        return contribution, 201


class CloseContributionResource(Resource):
    @marshal_with(contribution_fields)   
    def post(self):      
        parsed_args = closeContributionParser.parse_args()  
        payload = parse_token(request)
        userId = payload['sub'] 
        contributionId = parsed_args['id'] 
        userObj = getUser(userId)  
        if not userObj:
            abort(404, message="User who is closing contribution {} doesn't exist".format(userId)) 
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == contributionId).first()
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(contributionId))
        if contributionObject.status != 'Open':
            abort(404, message="Contribution {} is already closed".format(contributionId))        
        if userObj.id != contributionObject.userId:
            abort(404, message="Only contribution userId can close this contribution".format(userId)) 
        
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
            organizationId = 1
        contributionObject = session.query(cls.Contribution).filter(cls.UserOrganization.organization_id == organizationId).filter(cls.Contribution.users_organizations_id ==cls.UserOrganization.id).all()
        return contributionObject
    
class ContributionStatusResource(Resource):
    @marshal_with(contribution_status_fields)
    def get(self,id):
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        print 'got Get for Contribution fbid:'+id
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(id))
        payload = parse_token(request)
        userId = payload['sub'] 
        userOrgObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == userId).filter(cls.UserOrganization.organization_id == contributionObject.userOrganization.organization_id).first()
        userOrgObjs = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == contributionObject.userOrganization.organization_id).all()
        contributionValues = session.query(cls.ContributionValue).filter(cls.ContributionValue.contribution_id == contributionObject.id).filter(cls.ContributionValue.users_organizations_id == userOrgObj.id).first()
        
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
        for contributor in contributionObject.contributors:
            contributor.name= getUser(contributor.contributor_id).name
            contributor.imgUrl= getUser(contributor.contributor_id).imgUrl
            contributor.real_name= getUser(contributor.contributor_id).real_name
            contributorUserOrgObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == contributor.contributor_id).filter(cls.UserOrganization.organization_id == contributionObject.userOrganization.organization_id).first()
            contributor.project_reputation = contributorUserOrgObj.org_reputation
        bids = contributionObject.bids
        bids.sort(key=lambda x: x.time_created, reverse=False)
        for bid in bids:
            bid.date = bid.time_created.date()
            bid.contributionValueAfterBid = bid.contribution_value_after_bid
            last_bid = bid
            groupWeight = groupWeight + bid.weight
            if(str(bid.userId) == str(userId)):
                myWeight = bid.weight 
                #reputationDelta = userOrgObj.org_reputation - bid.reputation
                myValuation = bid.tokens
            if (last_bid):
                currentValuation = last_bid.contribution_value_after_bid
                if contributionObject.currentValuation == 0 and currentValuation != 0 :
                    contributionObject.currentValuation = currentValuation
                    contributionObject.valueIndic = 1
        if not contributionValues:
            contributionObject.myReputationDelta = 0
        else :
            contributionObject.myReputationDelta = contributionValues.reputationGain
        
        contributionObject.myEvaluation = myValuation
        contributionObject.myWeight = myWeight
        contributionObject.groupWeight = groupWeight
        contributionObject.project_reputation = userOrgObj.org_reputation
        contributionObject.tokenName = contributionObject.userOrganization.organization.token_name
        contributionObject.code = contributionObject.userOrganization.organization.code
        return contributionObject
    
class MemberStatusAllOrgsResource(Resource):
    @marshal_with(member_status_fields)
    def get(self,userId):        
        userOrgObjs = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == cls.User.id).filter(cls.User.slackId == userId).all()
        userOrgObj = userOrgObjs[0]
        allContributions = session.query(cls.Contribution).all()
        allContributionValues = session.query(cls.ContributionValue).filter(cls.ContributionValue.users_organizations_id == cls.UserOrganization.id).filter(cls.UserOrganization.user_id == cls.User.id).filter(cls.User.slackId == userId).all()
        contributionsDict = {}
        for allContributionValue in allContributionValues :
            contributionsDict[allContributionValue.contribution_id] = allContributionValue.reputationGain
        currentValuation = 0
        myWeight = 0
        userOrgObj.name = userOrgObj.user.name
        userOrgObj.fullName = userOrgObj.user.real_name
        userOrgObj.imgUrl= userOrgObj.user.imgUrl72
        countOfContribution = 0  
        userOrgObj.reputationPercentage = 'N/A'
        projectDic = {}
        last_bid = None
        for contribution in allContributions:
            contributedCounted = False
            if(str(contribution.userId) == str(userOrgObj.user.id)):
                projectDic[contribution.userOrganization.organization.id] = contribution.userOrganization.organization
                countOfContribution = countOfContribution + 1
                contributedCounted = True
            if contributedCounted == False:
                for contributionContributor in contribution.contributors :
                    if(str(contributionContributor.contributor_id) == str(userOrgObj.user.id)):
                        projectDic[contribution.userOrganization.organization.id] = contribution.userOrganization.organization
                        countOfContribution = countOfContribution + 1
                        contributedCounted = True
            if contributedCounted == True:
                last_bid = None
                currentValuation = 0
                myWeight = 0
                #reputationDelta = 0
                bids = contribution.bids
                #reputationDelta = 0
                bids.sort(key=lambda x: x.time_created, reverse=False)
                for bid in bids:
                    last_bid = bid
                    if(str(bid.userId) == str(userOrgObj.user.id)):
                        myWeight = bid.weight 
                        #reputationDelta = userOrgObj.org_reputation - bid.reputation
                if (last_bid):
                    currentValuation = last_bid.contribution_value_after_bid
                contribution.currentValuation = currentValuation
                contribution.reputationDelta = contributionsDict[contribution.id]
                #contribution.reputationDelta = reputationDelta
                contribution.myWeight = myWeight
                contribution.tokenName= contribution.userOrganization.organization.token_name
                contribution.cTime = contribution.time_created.date()
                if userOrgObj.id != contribution.userOrganization.id :
                    userOrgObj.contributions.append(contribution)
        for contribution in userOrgObj.contributions:
            print 'contribution.myWeight'+str(contribution.myWeight)
        projects = []
        for key, value in projectDic.iteritems():
            projects.append(value)
        userOrgObj.contributionLength = countOfContribution
        userOrgObj.projects = projects
        userOrgObj.org_tokens = 'N/A'
        userOrgObj.org_reputation = 'N/A'
        return userOrgObj    


class MemberStatusResource(Resource):
    @marshal_with(member_status_fields)
    def get(self,userId,orgId):        
        userOrgObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == cls.User.id).filter(cls.User.slackId == userId).filter(cls.UserOrganization.organization_id == orgId).first()
        userOrgObjs = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == orgId).all()
        allContributions = session.query(cls.Contribution).filter(cls.UserOrganization.id == cls.Contribution.users_organizations_id).filter(cls.UserOrganization.organization_id == orgId).all()
        allContributionValues = session.query(cls.ContributionValue).filter(cls.ContributionValue.users_organizations_id == userOrgObj.id).all()
        contributionsDict = {}
        for allContributionValue in allContributionValues :
            contributionsDict[allContributionValue.contribution_id] = allContributionValue.reputationGain
        totalReputation = 0;
        for userOrgObjVar in userOrgObjs:
            totalReputation = totalReputation + userOrgObjVar.org_reputation
        currentValuation = 0
        myWeight = 0
        reputationDelta = 0
        userOrgObj.name = userOrgObj.user.name
        userOrgObj.fullName = userOrgObj.user.real_name
        userOrgObj.imgUrl= userOrgObj.user.imgUrl72
        
        userOrgObj.reputationPercentage = (userOrgObj.org_reputation / totalReputation)*100
        userOrgObj.tokens = userOrgObj.org_tokens
        userOrgObj.reputation = userOrgObj.org_reputation
        userOrgObj.tokenName = userOrgObj.organization.token_name
        userOrgObj.code = userOrgObj.organization.code
        last_bid = None
        countOfContribution = 0       
        for contribution in allContributions:
            contributedCounted = False
            if(str(contribution.userId) == str(userOrgObj.user.id)):
                countOfContribution = countOfContribution + 1
                contributedCounted = True
            if contributedCounted == False:
                for contributionContributor in contribution.contributors :
                    if(str(contributionContributor.contributor_id) == str(userOrgObj.user.id)):
                        countOfContribution = countOfContribution + 1
                        contributedCounted = True
            if contributedCounted == True:
                last_bid = None
                currentValuation = 0
                myWeight = 0
                bids = contribution.bids
                #reputationDelta = 0
                bids.sort(key=lambda x: x.time_created, reverse=False)
                for bid in bids:
                    last_bid = bid
                    if(str(bid.userId) == str(userOrgObj.user.id)):
                        myWeight = bid.weight 
                        #reputationDelta = userOrgObj.org_reputation - bid.reputation
                if (last_bid):
                    currentValuation = last_bid.contribution_value_after_bid
                contribution.currentValuation = currentValuation
                contribution.reputationDelta = contributionsDict[contribution.id]
                contribution.myWeight = myWeight
                contribution.cTime = contribution.time_created.date()
                contribution.tokenName= contribution.userOrganization.organization.token_name
                if(str(contribution.userId) != str(userOrgObj.user.id)):
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
            return {"channleOrgExists":"true","userOrgId":userOrgObj.id,"orgId":orgObj.id,"channelName":orgObj.channelName}    
         
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
        channelInfo = getChannelInfo(json['slackAccessToken'],json['channelId'])
        channelName = channelInfo['name']
        payload = parse_token(request)
        slackTeamId = payload['slackTeamId']
        orgObj = session.query(cls.Organization).filter(cls.Organization.slack_teamid == slackTeamId).filter(cls.Organization.channelId == json['channelId']).first()
        if orgObj:
            abort(404, message="Project for channelName {} already exist".format(channelName))
        orgObj = session.query(cls.Organization).filter(cls.Organization.slack_teamid == slackTeamId).filter(cls.Organization.code == json['code']).first()
        if orgObj:
            abort(404, message="Project with code {} already exist".format(json['code']))
        
        orgObj = session.query(cls.Organization).filter(cls.Organization.slack_teamid == slackTeamId).filter(cls.Organization.token_name == json['token_name']).first()
        if orgObj:
            abort(404, message="Project with token {} already exist".format(json['token_name']))
        
        
        #channelId = createChannel(json['channelName'])
        jsonStr = {"token_name":json['token_name'],
                    "slack_teamid":slackTeamId,"a":json['similarEvaluationRate'],"b":json['passingResponsibilityRate'],
                    "code":json['code'],"channelName":channelName,"channelId":json['channelId']}
        userOrgObj = cls.UserOrganization(jsonStr,session)  
        organization = cls.Organization(jsonStr,session)
        organization.name = channelName
        session.add(organization)
        session.flush()            
        usersDic = createUserAndUserOrganizations(organization.id,json['contributors'],json['initialTokens'],json['passingResponsibilityRate'],json['slackAccessToken'])
        
        
        contribution = cls.Contribution()
        contribution.min_reputation_to_close = 0
        #contribution.description = 'Founding Contribution'
        contribution.title = 'Founding Contribution'
        
        session.add(contribution)    
        session.flush()
        perc = 0
        for contributor in json['contributors']:
            contributionContributor = cls.ContributionContributor()
            contributionContributor.contributor_id = usersDic[contributor['id']]
            contributionContributor.contribution_id=contribution.id
            contributionContributor.percentage=contributor['percentage']
            if float(contributor['percentage']) > perc :
                perc = float(contributor['percentage'])
                contribution.userId = contributionContributor.contributor_id
            contribution.contributors.append(contributionContributor)  
        userOrgObjectForOwner = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == contribution.userId).filter(cls.UserOrganization.organization_id == organization.id).first()
        userOrgObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == organization.id).all()
        contribution.users_organizations_id = userOrgObjectForOwner.id
        for userOrgObject in userOrgObjects :
              contributionValue = cls.ContributionValue()
              contributionValue.user_id = userOrgObject.user_id
              contributionValue.users_organizations_id = userOrgObject.id
              contributionValue.contribution_id = contribution.id
              contributionValue.reputationGain = 0
              contributionValue.reputation = userOrgObject.org_reputation
              contributionValue.user_id = userOrgObject.user_id
              session.add(contributionValue)
              session.flush()
        stake = 0
        if slackTeamId == 'T02H16QH6' :
            stake = userOrgObjectForOwner.org_reputation*2/100
        else :
            stake = userOrgObjectForOwner.org_reputation*5/100
        jsonStr = {"tokens":json['initialTokens'],
                   "reputation":userOrgObjectForOwner.org_reputation,
                   "userId":contribution.userId,
                   "contribution_id":contribution.id,
                   "stake":stake, 
                   "time_created":datetime.now()
                    }

        bid = cls.Bid(jsonStr,session) 
        vd = ValueDistributer()
        vd.process_bid(bid,session)
        if(vd.error_occured):
            print vd.error_code
            # ToDo :  pass correct error message to user
            abort(404, message="Failed to process bid".format(contribution.id))
        
        
              
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
                    for contributor in contributionObject.contributors:
                        session.delete(contributor)
                    for bid in contributionObject.bids:
                        session.delete(bid)
                    session.delete(contributionObject)
                session.delete(userOrganization)        
            session.delete(orgObj)
            session.commit()
        return {}, 204
    
def getSlackUsers(slackAccessToken):
    print 'slackAccessToken'+slackAccessToken
    team_users_api_url = 'https://slack.com/api/users.list'
    headers = {'User-Agent': 'DEAP'}
    r = requests.get(team_users_api_url, params={'token':slackAccessToken}, headers=headers)
    users = json.loads(r.text)['members']
    print 'slack users:'+str(users)
    return users

def getChannelInfo(slackAccessToken,channelId):
    print 'slackAccessToken'+slackAccessToken
    channel_info_api_url = 'https://slack.com/api/channels.info'
    headers = {'User-Agent': 'DEAP'}
    r = requests.get(channel_info_api_url, params={'token':slackAccessToken,'channel':channelId}, headers=headers)
    channelInfo = json.loads(r.text)['channel']
    print 'channelInfo is:'+str(channelInfo)
    return channelInfo
    
class getAllSlackUsersResource(Resource):
    def post(self):
        print 'comes here'
        json = request.json
        slackAccessToken = json['slackAccessToken']
        userIds = json['userIds']
        searchString = json['searchString']
        
        users = getSlackUsers(slackAccessToken)
        usersJson = []
        userIdsList = []
        if userIds != '':
            userIdsList = userIds.split(",")
        
        for user in users :
            realName = user['profile']['real_name']
            slackUserId = user['id']
            userName= user['name']
            if user['deleted'] == True :
                continue
            if user['is_bot'] == True :
                continue
            if searchString != '':
                if  searchString.lower()  not in realName.lower() and searchString.lower()  not in userName.lower():
                    continue
            if len(userIdsList) > 0 :
                if slackUserId in userIdsList:   
                    continue
            jsonStr = {"id":user['id'],"name":user['name'],"imgUrl":user['profile']['image_48'],"real_name":user['profile']['real_name']}
            usersJson.append(jsonStr)
        return usersJson
    
def createChannel(channelName,slackAccessToken):
        team_users_api_url = 'https://slack.com/api/channels.create'
        headers = {'User-Agent': 'DEAP'}
        r = requests.post(team_users_api_url, params={'token':slackAccessToken,'name':channelName}, headers=headers)
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
        
        
    
def createUserAndUserOrganizations(organizaionId,contributors,token,b,slackAccessToken):
    
    usersInSystem = session.query(cls.User).all()
    contributionDic = {}
    for contributor in contributors :
        contributionDic[contributor['id']] = (float(token)/100)*float(contributor['percentage'])
    usersDic = {}
    for u in usersInSystem:
        usersDic[u.slackId] = u.id
    # parse response:
    users = getSlackUsers(slackAccessToken)
    print 'slack users:'+str(users)
    for user in users :
        token = 0
        reputation = 0
        try:
            #token = contributionDic[user['id']]
            #reputation = (int(token))*10/pow(10,(int(b)/50)) 
            token = 0
            reputation = 0
        except KeyError:
            token = 0
            reputation = 0
        userId = ''
        if user['deleted'] == True :
            continue
        if user['is_bot'] == True :
            continue
        try:
            userId = usersDic[user['id']]
        except KeyError:
            userId = ''
        if userId == '':            
            jsonStr = {"name":user['name'],"slackId":user['id'],"imgUrl":user['profile']['image_48'],"imgUrl72":user['profile']['image_72'],"real_name":user['profile']['real_name']}
            u = cls.User(jsonStr,session)
            session.add(u) 
            session.flush() 
            userId = u.id
            usersDic[user['id']] = u.id
                         
        jsonStr = {"user_id":userId,
                    "organization_id":organizaionId,
                    "org_tokens":token,
                    "org_reputation":reputation
                    }
        userOrganization = cls.UserOrganization(jsonStr,session)
        session.add(userOrganization)  
        session.flush()  
    return usersDic     
    
  
    
def allContributionsFromUser(): 
    
    users_api_url = 'https://slack.com/api/auth.test'

    params = {
        'slackAccessToken': request.form['token'],
    }
    slackAccessToken = params["slackAccessToken"]
    channelId = request.form['channelId']
    headers = {'User-Agent': 'DEAP'}
    print 'slackAccessToken:'+str(slackAccessToken)

    # Step 2. Retrieve information about the current user.
    r = requests.get(users_api_url, params={'token':slackAccessToken}, headers=headers)
    profile = json.loads(r.text)
    print 'slack profile:'+str(profile)  
    contribitions = [];
    milestones = [];
    closedContribitions = [];
    closedMilestones = [];
    user = session.query(cls.User).filter(cls.User.slackId == profile['user_id']).first()
    if not user:
        return [] 
    orgObj = session.query(cls.Organization).filter(cls.Organization.channelId == channelId).filter(cls.Organization.slack_teamid == profile['team_id']).first()
    if not orgObj:
        return []
    userOrganizationObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == orgObj.id).filter(cls.UserOrganization.user_id == user.id).first()
    if not userOrganizationObj:
        return []
    allClosedContribution = session.query(cls.Contribution).filter(cls.Contribution.status == 'Closed').all()
    for contribution in allClosedContribution :
        milestoneObj = session.query(cls.Milestone).filter(cls.Milestone.contribution_id == contribution.id).first()
        if milestoneObj :
            closedMilestones.append(milestoneObj.id)
        else:
            closedContribitions.append(contribution.id)
       
    bidsList = session.query(cls.Bid).filter(cls.Bid.userId == user.id).filter(cls.Bid.contribution_id == cls.Contribution.id).all()
    for bid in bidsList:        
        milestoneObj = session.query(cls.Milestone).filter(cls.Milestone.contribution_id == bid.contribution_id).first()
        contributionObj = session.query(cls.Contribution).filter(cls.Contribution.id == bid.contribution_id).first()
        if milestoneObj :
             if contributionObj.status != 'Closed':
                 milestones.append(milestoneObj.id)
                
        else :
            if contributionObj.status != 'Closed':
                 contribitions.append(bid.contribution_id)
                
            
    
    jsonString = {'contribitions':contribitions,'milestones':milestones,'closedContribitions':closedContribitions,'closedMilestones':closedMilestones}
    return jsonString


def allChannelIdsForTeam(): 
    slackTeamId = request.form['team']
    orgs = session.query(cls.Organization).filter(cls.Organization.slack_teamid == slackTeamId).all()
    orgChannelId = ''
    count = 1
    for org in orgs:
            if count == 1:
                orgChannelId = org.channelId
            else:
                orgChannelId = orgChannelId + ','+ org.channelId
            count = count + 1;
    return orgChannelId

def showreservetokens(): 
    slackTeamId = request.form['team_id']
    channelId = request.form['channel_id']
    print 'slackTeamId is'+str(slackTeamId)
    print 'channelId is'+str(channelId)
    if(slackTeamId != '' and  channelId != ''):
        orgObj = session.query(cls.Organization).filter(cls.Organization.slack_teamid == slackTeamId).filter(cls.Organization.channelId == channelId).first()
    if not orgObj:
            return "No Project Exists"
    else:
           return 'Reserved Token for this channel is: '+str(orgObj.reserveTokens)
    



class MilestoneResource(Resource):
    @marshal_with(milestone_fields)
    def get(self, id):
        milestoneObject = session.query(cls.Milestone).filter(cls.Milestone.id == id).first()
        print 'got Get for Milestone fbid:'+id
        if not milestoneObject:
            abort(404, message="Milestone {} doesn't exist".format(id))
        userOrgObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == milestoneObject.userOrganization.organization_id).all()
        usersReputationDic = {}
        for userOrgObject in userOrgObjects:
            usersReputationDic[userOrgObject.user_id]=userOrgObject.org_reputation
        for milestoneContributor in milestoneObject.contributors:
            milestoneContributor.name= getUser(milestoneContributor.contributor_id).name
            milestoneContributor.real_name= getUser(milestoneContributor.contributor_id).real_name
            milestoneContributor.imgUrl= getUser(milestoneContributor.contributor_id).imgUrl
        milestoneObject.current_org_id = milestoneObject.userOrganization.organization_id
        milestoneObject.channelName = milestoneObject.userOrganization.organization.channelName
        milestoneObject.code = milestoneObject.userOrganization.organization.code
        milestoneObject.tokenName = milestoneObject.userOrganization.organization.token_name
        for milestoneContribution in milestoneObject.contributions:
            countOfLines = 0
            shortDescription = '';
            milestoneContributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == milestoneContribution.contribution_id).first()
            if milestoneContributionObject.description != None :
                for line in milestoneContributionObject.description.splitlines():
                    countOfLines = countOfLines + 1
                    if(shortDescription != ''):
                        shortDescription = shortDescription  + '\n'
                    shortDescription = shortDescription + line
                    if countOfLines == 3 :
                        shortDescription = shortDescription + '....'
                        break    
            
                   
            contributionContributorsObjs =milestoneContributionObject.contributors
            finalCountOfContributors = 0
            for contributionContributorsObj in contributionContributorsObjs:
                finalCountOfContributors = finalCountOfContributors + 1
                contributionContributorsObj.reputation = usersReputationDic[contributionContributorsObj.contributor_id]                
            contributionContributorsObjs.sort(key=lambda x: x.reputation, reverse=True)
            totalCountOfContrbutors = 0
            milestoneContribution.contributors = []
            for contributionContributorsObj in contributionContributorsObjs:
                totalCountOfContrbutors = totalCountOfContrbutors +1
                contributionContributorsObj.memberId = getUser(contributionContributorsObj.contributor_id).slackId
                contributionContributorsObj.imgUrl= getUser(contributionContributorsObj.contributor_id).imgUrl
                contributionContributorsObj.displayName= getUser(contributionContributorsObj.contributor_id).name
                contributionContributorsObj.id = contributionContributorsObj.contributor_id
                milestoneContribution.contributors.append(contributionContributorsObj)
                print 'contributionContributorsObj.reputation'+str(contributionContributorsObj.reputation)
                if totalCountOfContrbutors == 8 :
                    break
            milestoneContribution.remainingContributors = finalCountOfContributors - totalCountOfContrbutors
            milestoneContribution.title= milestoneContributionObject.title
            milestoneContribution.date= milestoneContributionObject.time_created.date()
            milestoneContribution.description = shortDescription
            currentValuation = 0
            last_bid = None
            bids = milestoneContributionObject.bids
            bids.sort(key=lambda x: x.time_created, reverse=False)
            for bid in bids:
                last_bid = bid
            if (last_bid):
                currentValuation = last_bid.contribution_value_after_bid
            milestoneContribution.valuation = currentValuation
        return milestoneObject

    def delete(self, id):
        milestoneObject = session.query(cls.Milestone).filter(cls.Milestone.id == id).first()
        if not milestoneObject:
            abort(404, message="Milestone {} doesn't exist".format(id))
        for milestoneContributor in milestoneObject.contributors:
            session.delete(milestoneContributor)
        for milestoneBid in milestoneObject.milestoneBids:
            session.delete(milestoneBid)
        for milestoneContribution in milestoneObject.contributions:
            session.delete(milestoneContribution)
        session.delete(milestoneObject)
        session.commit()
        return {}, 204
    
    @marshal_with(milestone_fields)   
    def post(self): 
        json = request.json         
        milestone = cls.Milestone()
        milestone.description = json['description']
        milestone.title = json['title']
        payload = parse_token(request)
        userId = payload['sub']
        orgObject = session.query(cls.Organization).filter(cls.Organization.channelId == json['channelId']).first()
        slackTeamId = orgObject.slack_teamid
        if slackTeamId == 'T02H16QH6' and userId != 79 :
            abort ("User {} cannot create milestone".format(userId))
        userOrgObjectForOwner = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == orgObject.id).filter(cls.UserOrganization.user_id == userId).first()
        milestone.users_organizations_id = userOrgObjectForOwner.id
        milestone.destination_org_id = json['evaluatingProject']
        destOrgObject = session.query(cls.Organization).filter(cls.Organization.id == json['evaluatingProject']).first()
        milestone.destChannelId = destOrgObject.channelId
        milestone.destChannelName = destOrgObject.channelName
        session.add(milestone)
        session.flush()
        totalContributions = 0
        totalValue = 0
        totalTokens = 0    
        contributorsDic = {}        
        userOrgObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == userOrgObjectForOwner.organization_id).all()
        for userOrgObject in userOrgObjects:
            totalTokens = totalTokens + userOrgObject.org_tokens
            if userOrgObject.org_tokens > 0 :
                contributorsDic[userOrgObject.user.id] = userOrgObject.org_tokens
            userOrgObject.org_tokens = 0
            session.add(userOrgObject)
            
        milestone.tokens = totalTokens
        allContributionObjects = session.query(cls.Contribution).filter(cls.Contribution.status == 'Open').filter(cls.Contribution.users_organizations_id == cls.UserOrganization.id).filter(cls.UserOrganization.organization_id == userOrgObjectForOwner.organization_id).all()
        
        
        for contribution in allContributionObjects:
            totalContributions = totalContributions + 1 
            last_bid = None
            currentValuation = 0
            bids = contribution.bids
            bids.sort(key=lambda x: x.time_created, reverse=False)
            for bid in bids:
                last_bid = bid
            if (last_bid):
                currentValuation = last_bid.contribution_value_after_bid
            totalValue = totalValue + currentValuation             
            milestoneContribution = cls.MilestoneContribution()
            milestoneContribution.contribution_id = contribution.id
            milestoneContribution.milestone_id = milestone.id
            milestone.contributions.append(milestoneContribution) 
            contribution.status='Closed'
            session.add(contribution)
         
        milestone.totalValue =  totalValue
        perc = 0
        userId = ''
        for key, elem in contributorsDic.items():
            milestoneContributor = cls.MilestoneContributor()
            milestoneContributor.milestone_id = milestone.id
            milestoneContributor.contributor_id = key
            milestoneContributor.percentage = round(float((elem/totalTokens)*100),0)
            if float(milestoneContributor.percentage) > perc:
                perc = float(milestoneContributor.percentage)
                userId = milestoneContributor.contributor_id
            milestone.contributors.append(milestoneContributor)
        userOrgObjectForTargetOwner = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == userId).filter(cls.UserOrganization.organization_id == json['evaluatingProject']).first()
        contribution = cls.Contribution()
        contribution.userId = userId
        milestone.userId = userId
        contribution.min_reputation_to_close = 0
        contribution.description = json['description']
        contribution.title = json['title']
        contribution.users_organizations_id = userOrgObjectForTargetOwner.id
        session.add(contribution)
        session.flush()
        for contributor in milestone.contributors:             
            contributionContributor = cls.ContributionContributor()
            contributionContributor.contributor_id = contributor.contributor_id
            contributionContributor.contribution_id=contribution.id
            contributionContributor.percentage=contributor.percentage
            contribution.contributors.append(contributionContributor)  
        
        session.add(contribution)
        milestone.contribution_id =  contribution.id 
        
        userOrgObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == json['evaluatingProject']).all()
        for userOrgObject in userOrgObjects :
              contributionValue = cls.ContributionValue()
              contributionValue.user_id = userOrgObject.user_id
              contributionValue.users_organizations_id = userOrgObject.id
              contributionValue.contribution_id = contribution.id
              contributionValue.reputationGain = 0
              contributionValue.reputation = userOrgObject.org_reputation
              contributionValue.user_id = userOrgObject.user_id
              session.add(contributionValue)
                
        session.commit()  
        for contributor in milestone.contributors:             
            contributor.id = contributor.contributor_id
        return milestone, 201

    
    
    
class OrganizationCurrentStatusResource(Resource):
    @marshal_with(milestone_fields)
    def get(self, orgId):
        milestone = cls.Milestone()
        totalTokens = 0
        userOrgObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == orgId).all()
        usersReputationDic = {}
        contributorsDic = {}
        orgObject = session.query(cls.Organization).filter(cls.Organization.id == orgId).first()
        for userOrgObject in userOrgObjects:
            totalTokens = totalTokens + userOrgObject.org_tokens
            usersReputationDic[userOrgObject.user_id]=userOrgObject.org_reputation
            if userOrgObject.org_tokens > 0 :
                contributorsDic[userOrgObject.user_id]=userOrgObject.org_tokens
            
        milestone.tokens = totalTokens
        milestone.code = orgObject.code
        milestone.tokenName = orgObject.token_name
        milestone.channelName = orgObject.channelName
        allContributionObjects = session.query(cls.Contribution).filter(cls.Contribution.status == 'Open').filter(cls.Contribution.users_organizations_id == cls.UserOrganization.id).filter(cls.UserOrganization.organization_id == orgId).all()
        
        totalContributions = 0
        totalValue = 0
        for contribution in allContributionObjects:
            shortDescription = ''
            countOfLines = 0
            if contribution.description != None :
                for line in contribution.description.splitlines():
                    countOfLines = countOfLines + 1
                    if(shortDescription != ''):
                        shortDescription = shortDescription  + '\n'
                    shortDescription = shortDescription + line
                    if countOfLines == 3 :
                        shortDescription = shortDescription + '....'
                        break
            
            totalContributions = totalContributions + 1 
            last_bid = None
            currentValuation = 0
            bids = contribution.bids
            bids.sort(key=lambda x: x.time_created, reverse=False)
            for bid in bids:
                last_bid = bid
            if (last_bid):
                currentValuation = last_bid.contribution_value_after_bid
            
            totalValue = totalValue + currentValuation             
            milestoneContribution = cls.MilestoneContribution()
            milestoneContribution.valuation = currentValuation
            milestoneContribution.description = shortDescription
            contributionContributorsObjs = contribution.contributors
            finalCountOfContributors = 0
            for contributionContributorsObj in contributionContributorsObjs:
                finalCountOfContributors = finalCountOfContributors + 1
                contributionContributorsObj.reputation = usersReputationDic[contributionContributorsObj.contributor_id]
                
            contributionContributorsObjs.sort(key=lambda x: x.reputation, reverse=True)
            totalCountOfContrbutors = 0
            milestoneContribution.contributors = []
            for contributionContributorsObj in contributionContributorsObjs:
                totalCountOfContrbutors = totalCountOfContrbutors +1
                contributionContributorsObj.memberId = getUser(contributionContributorsObj.contributor_id).slackId
                contributionContributorsObj.imgUrl= getUser(contributionContributorsObj.contributor_id).imgUrl
                contributionContributorsObj.displayName= getUser(contributionContributorsObj.contributor_id).name
                milestoneContribution.contributors.append(contributionContributorsObj)
                print 'contributionContributorsObj.reputation'+str(contributionContributorsObj.reputation)
                if totalCountOfContrbutors == 8 :
                    break
            milestoneContribution.remainingContributors = finalCountOfContributors - totalCountOfContrbutors
            milestoneContribution.contribution_id = contribution.id
            milestoneContribution.title= contribution.title
            milestoneContribution.date= contribution.time_created.date()
            milestone.contributions.append(milestoneContribution) 
         
        milestone.totalValue =  totalValue
        for key, elem in contributorsDic.items():
            milestoneContributor = cls.MilestoneContributor()
            milestoneContributor.id = key
            milestoneContributor.percentage = round(float((elem/totalTokens)*100),0)
            milestoneContributor.name= getUser(milestoneContributor.id).name
            milestoneContributor.real_name= getUser(milestoneContributor.id).real_name
            milestoneContributor.imgUrl= getUser(milestoneContributor.id).imgUrl
            milestone.contributors.append(milestoneContributor)
        return milestone


class AllMilestonesForOrgResource(Resource):
    def get(self, id):
        allMilestoneObjects = session.query(cls.Milestone).filter(cls.Milestone.users_organizations_id == cls.UserOrganization.id).filter(cls.UserOrganization.organization_id == id).all()
        milestonesJson = []
        for milestone in allMilestoneObjects:
            jsonStr = {"id":milestone.id,"title":milestone.title}
            milestonesJson.append(jsonStr)
        return milestonesJson