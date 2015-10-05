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
milestoneParser = reqparse.RequestParser()
bidParser = reqparse.RequestParser()
mileStonebidParser = reqparse.RequestParser()
closeContributionParser = reqparse.RequestParser()


milestoneParser.add_argument('users_organizations_id', type=int,required=True)
milestoneParser.add_argument('description', type=str,required=True)
milestoneParser.add_argument('title', type=str)
milestoneParser.add_argument('evaluatingTeam', type=int,required=True)

userParser.add_argument('userId', type=str)
userParser.add_argument('name', type=str,required=True)
userParser.add_argument('slack_id', type=str)


bidParser.add_argument('tokens', type=str,required=True)
bidParser.add_argument('contribution_id', type=str,required=True)
bidParser.add_argument('ownerId', type=int,required=True)

mileStonebidParser.add_argument('stake', type=str,required=True)
mileStonebidParser.add_argument('tokens', type=str,required=True)
mileStonebidParser.add_argument('reputation', type=str,required=True)    
mileStonebidParser.add_argument('milestone_id', type=str,required=True)
mileStonebidParser.add_argument('ownerId', type=int,required=True)

closeContributionParser.add_argument('ownerId', type=int,required=True)
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
bid_nested_fields['ownerId'] = fields.Integer
bid_nested_fields['bidderName'] = fields.String

bid_status_nested_fields = {}
bid_status_nested_fields['time_created'] = fields.String
bid_status_nested_fields['tokens'] = fields.String
bid_status_nested_fields['reputation'] = fields.String
bid_status_nested_fields['contribution_value_after_bid'] = fields.Float
bid_status_nested_fields['stake'] = fields.Float
bid_status_nested_fields['ownerId'] = fields.Integer

contributor_nested_fields = {}
contributor_nested_fields['id'] = fields.String
contributor_nested_fields['percentage'] = fields.String
contributor_nested_fields['name'] = fields.String
contributor_nested_fields['real_name'] = fields.String
contributor_nested_fields['url'] = fields.String
contributor_nested_fields['project_reputation'] = fields.String

contribution_fields = {}
contribution_fields['id'] = fields.Integer
contribution_fields['time_created'] = fields.DateTime
contribution_fields['users_organizations_id'] = fields.Integer
contribution_fields['status'] = fields.String
contribution_fields['ownerId'] = fields.String
contribution_fields['file'] = fields.String
contribution_fields['title'] = fields.String
contribution_fields['tokenName'] = fields.String
contribution_fields['code'] = fields.String
contribution_fields['channelId'] = fields.String
contribution_fields['currentValuation'] = fields.Integer
contribution_fields['bids'] = fields.Nested(bid_nested_fields)
contribution_fields['contributionContributors'] = fields.Nested(contributor_nested_fields)

contribution_status_fields ={}
contribution_status_fields['currentValuation'] = fields.Float
contribution_status_fields['valueIndic'] = fields.Integer
contribution_status_fields['reputationDelta'] = fields.Integer
contribution_status_fields['myValuation'] = fields.Integer
contribution_status_fields['myWeight'] = fields.Float
contribution_status_fields['groupWeight'] = fields.Float
contribution_status_fields['project_reputation'] = fields.Float
contribution_status_fields['totalSystemReputation'] = fields.Float
contribution_status_fields['file'] = fields.String
contribution_status_fields['title'] = fields.String
contribution_status_fields['bids'] = fields.Nested(bid_status_nested_fields)
contribution_status_fields['contributionContributors'] = fields.Nested(contributor_nested_fields)

contribution_status_nested_fields ={}
contribution_status_nested_fields['currentValuation'] = fields.Integer
contribution_status_nested_fields['reputationDelta'] = fields.Integer
contribution_status_nested_fields['id'] = fields.Integer
contribution_status_nested_fields['myWeight'] = fields.Float
contribution_status_nested_fields['title'] = fields.String
contribution_status_nested_fields['cTime'] = fields.String
contribution_status_nested_fields['tokenName'] = fields.String
contribution_status_nested_fields['ownerId'] = fields.String


member_status_fields ={}
member_status_fields['project_tokens'] = fields.String
member_status_fields['tokenName'] = fields.String
member_status_fields['code'] = fields.String
member_status_fields['project_reputation'] = fields.String
member_status_fields['contributionLength'] = fields.String
member_status_fields['url'] = fields.String
member_status_fields['fullName'] = fields.String
member_status_fields['name'] = fields.String
member_status_fields['reputationPercentage'] = fields.String
member_status_fields['contributions'] = fields.Nested(contribution_status_nested_fields)



milestoneContributor_nested_fields = {}
milestoneContributor_nested_fields['id'] = fields.String
milestoneContributor_nested_fields['percentage'] = fields.String
milestoneContributor_nested_fields['name'] = fields.String
milestoneContributor_nested_fields['real_name'] = fields.String
milestoneContributor_nested_fields['url'] = fields.String

contribution_contributor_nested_fields = {}
contribution_contributor_nested_fields['memberId'] = fields.String
contribution_contributor_nested_fields['url'] = fields.String

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
milestone_fields['ownerId'] = fields.String
milestone_fields['description'] = fields.String
milestone_fields['tokens'] = fields.Float
milestone_fields['totalValue'] = fields.Float
milestone_fields['contributions'] = fields.Integer
milestone_fields['contributors'] = fields.Integer
milestone_fields['title'] = fields.String
milestone_fields['tokenName'] = fields.String
milestone_fields['channelName'] = fields.String
milestone_fields['code'] = fields.String
milestone_fields['destination_org_id'] = fields.Integer
milestone_fields['milestoneContributors'] = fields.Nested(milestoneContributor_nested_fields)
milestone_fields['milestoneContributions'] = fields.Nested(milestoneContribution_nested_fields)



def getUser(id):
    user = session.query(cls.User).filter(cls.User.id == id).first()    
    return user

def getUserBySlackId(id):
    user = session.query(cls.User).filter(cls.User.slackId == id).first()    
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
        userObj = getUser(parsed_args['ownerId'])        
        if not userObj:
            abort(404, message="User {} who is creating bid  doesn't exist".format(parsed_args['ownerId']))
        contributionValues = session.query(cls.ContributionValue).filter(cls.ContributionValue.contribution_id == contributionObject.id).filter(cls.ContributionValue.users_organizations_id == cls.UserOrganization.id).filter(cls.UserOrganization.user_id == userObj.id).filter(cls.UserOrganization.organization_id == contributionObject.userOrganization.organization_id).first()  
        jsonStr = {"tokens":parsed_args['tokens'],
                   "reputation":contributionValues.reputation,
                   "ownerId":parsed_args['ownerId'],
                   "contribution_id":parsed_args['contribution_id'],
                   "stake":contributionValues.reputation*5/100, 
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
    
class MileStoneBidResource(Resource):
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
        parsed_args = mileStonebidParser.parse_args()
        mileStoneId = parsed_args['milestone_id']        
        mileStoneObject = session.query(cls.MileStone).filter(cls.MileStone.id == mileStoneId).first()
        if not mileStoneObject:
            abort(404, message="MileStone {} doesn't exist".format(mileStoneId)) 
        contributionid = mileStoneObject.contribution_id     
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == contributionid).first()
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(contributionid))
        if contributionObject.status != 'Open':
            abort(404, message="Contribution {} is not Open".format(contributionid))
        userObj = getUser(parsed_args['ownerId'])        
        if not userObj:
            abort(404, message="User {} who is creating bid  doesn't exist".format(parsed_args['ownerId']))     
        jsonStr = {"tokens":parsed_args['tokens'],
                   "reputation":parsed_args['reputation'],
                   "ownerId":parsed_args['ownerId'],
                   "contribution_id":contributionid,
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
        char = session.query(cls.Bid).filter(cls.Bid.contribution_id == contributionId).filter(cls.Bid.ownerId == userId).first()   
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == contributionId).first() 
        if contributionObject.status == 'Closed':
            return {"contributionClose":"true"}  
        if not char:
            return {"contributionClose":"false","bidExists":"false","organizationId":contributionObject.userOrganization.organization_id}
        else:
            return {"contributionClose":"false","bidExists":"true"} 
        
        
class MileStoneBidContributionResource(Resource):
    def get(self, mileStoneId,userId):
        milestoneObj = session.query(cls.MileStone).filter(cls.MileStone.id == mileStoneId).first()
        contributionId = milestoneObj.contribution_id
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == contributionId).first()
        char = session.query(cls.Bid).filter(cls.Bid.contribution_id == contributionId).filter(cls.Bid.ownerId == userId).first()
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
        for contributor in contributionObject.contributionContributors:
            contributor.name= getUser(contributor.contributor_id).name
            contributor.id = contributor.contributor_id
            
        last_bid = None 
        currentValuation = 0  
        bids = contributionObject.bids
        bids.sort(key=lambda x: x.time_created, reverse=False)    
        for bid in bids:
            bid.bidderName = getUser(bid.ownerId).name
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
        for contributor in contributionObject.contributionContributors:
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
        contribution.ownerId = json['ownerId']
        contribution.min_reputation_to_close = json['min_reputation_to_close']
        contribution.file = json['file']
        contribution.title = json['title']
        contribution.users_organizations_id = json['users_organizations_id']
        session.add(contribution) 
        session.flush()  
        userOrgObjectForOwner = session.query(cls.UserOrganization).filter(cls.UserOrganization.id == json['users_organizations_id']).first()
        userObj = getUser(contribution.ownerId) 
               
        if not userObj:
            abort(404, message="User who is creating contribution {} doesn't exist".format(contribution.ownerId))    
        for contributor in json['contributors']:             
            contributionContributor = cls.ContributionContributor()
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
            contribution.contributionContributors.append(contributionContributor)  
        if(len(contribution.contributionContributors) == 0):
            contributionContributor = cls.ContributionContributor()
            contributionContributor.contributor_id = contribution.ownerId
            contributionContributor.percentage = '100'
            contributionContributor.name = userObj.name
            contribution.contributionContributors.append(contributionContributor)  
            #if (firstContribution == True):
                #userOrgObjectForOwner.org_reputation = 100
                #session.add(userOrgObjectForOwner) 
                                
        #if((parsed_args['intialBid'].obj1['tokens'] != '') & (parsed_args['intialBid'].obj1['reputation'] != '')):      
                #jsonStr = {"tokens":parsed_args['intialBid'].obj1['tokens'],
                   #"reputation":parsed_args['intialBid'].obj1['reputation'],
                   #"ownerId":contribution.ownerId,
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
        for contributor in contribution.contributionContributors:             
            contributor.id=contributor.contributor_id
        contribution.channelId = userOrgObjectForOwner.organization.channelId
        return contribution, 201


class CloseContributionResource(Resource):
    @marshal_with(contribution_fields)   
    def post(self):      
        parsed_args = closeContributionParser.parse_args()   
        ownerId = parsed_args['ownerId'] 
        contributionId = parsed_args['id'] 
        userObj = getUser(ownerId)  
        if not userObj:
            abort(404, message="User who is closing contribution {} doesn't exist".format(ownerId)) 
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == contributionId).first()
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(contributionId))
        if contributionObject.status != 'Open':
            abort(404, message="Contribution {} is already closed".format(contributionId))        
        if userObj.id != contributionObject.ownerId:
            abort(404, message="Only contribution ownerId can close this contribution".format(ownerId)) 
        
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
    def get(self,id,userId):
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        print 'got Get for Contribution fbid:'+id
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(id))
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
        for contributor in contributionObject.contributionContributors:
            contributor.name= getUser(contributor.contributor_id).name
            contributor.url= getUser(contributor.contributor_id).url
            contributor.real_name= getUser(contributor.contributor_id).real_name
            contributorUserOrgObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == contributor.contributor_id).filter(cls.UserOrganization.organization_id == contributionObject.userOrganization.organization_id).first()
            contributor.project_reputation = contributorUserOrgObj.org_reputation
        bids = contributionObject.bids
        bids.sort(key=lambda x: x.time_created, reverse=False)
        for bid in bids:
            last_bid = bid
            groupWeight = groupWeight + bid.weight
            if(str(bid.ownerId) == str(userId)):
                myWeight = bid.weight 
                #reputationDelta = userOrgObj.org_reputation - bid.reputation
                myValuation = bid.tokens
            if (last_bid):
                currentValuation = last_bid.contribution_value_after_bid
                if contributionObject.currentValuation == 0 and currentValuation != 0 :
                    contributionObject.currentValuation = currentValuation
                    contributionObject.valueIndic = 1
        contributionObject.reputationDelta = contributionValues.reputationGain
        print 'contributionObject.reputationDelta'+str(contributionObject.reputationDelta)
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
        allContributionValues = session.query(cls.ContributionValue).filter(cls.ContributionValue.users_organizations_id == cls.UserOrganization.id).filter(cls.UserOrganization.user_id == cls.User.id).filter(cls.User.slackId == userId).filter(cls.UserOrganization.organization_id == cls.Organization.id).filter(cls.Organization.slack_teamid == slackTeamId).all()
        contributionsDict = {}
        for allContributionValue in allContributionValues :
            contributionsDict[allContributionValue.contribution_id] = allContributionValue.reputationGain
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
            if(str(contribution.ownerId) == str(userOrgObj.user.id)):
                countOfContribution = countOfContribution + 1
                contributedCounted = True
            if contributedCounted == False:
                for contributionContributor in contribution.contributionContributors :
                    if(str(contributionContributor.contributor_id) == str(userOrgObj.user.id)):
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
                    if(str(bid.ownerId) == str(userOrgObj.user.id)):
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
        userOrgObj.url = userOrgObj.user.url72
        
        userOrgObj.reputationPercentage = (userOrgObj.org_reputation / totalReputation)*100
        userOrgObj.project_tokens = userOrgObj.org_tokens
        userOrgObj.project_reputation = userOrgObj.org_reputation
        userOrgObj.tokenName = userOrgObj.organization.token_name
        userOrgObj.code = userOrgObj.organization.code
        last_bid = None
        countOfContribution = 0       
        for contribution in allContributions:
            contributedCounted = False
            if(str(contribution.ownerId) == str(userOrgObj.user.id)):
                countOfContribution = countOfContribution + 1
                contributedCounted = True
            if contributedCounted == False:
                for contributionContributor in contribution.contributionContributors :
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
                    if(str(bid.ownerId) == str(userOrgObj.user.id)):
                        myWeight = bid.weight 
                        #reputationDelta = userOrgObj.org_reputation - bid.reputation
                if (last_bid):
                    currentValuation = last_bid.contribution_value_after_bid
                contribution.currentValuation = currentValuation
                contribution.reputationDelta = contributionsDict[contribution.id]
                contribution.myWeight = myWeight
                contribution.cTime = contribution.time_created.date()
                contribution.tokenName= contribution.userOrganization.organization.token_name
                if(str(contribution.ownerId) != str(userOrgObj.user.id)):
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
        orgObj = session.query(cls.Organization).filter(cls.Organization.slack_teamid == json['slack_teamid']).filter(cls.Organization.code == json['code']).first()
        if orgObj:
            return {"codeExist":"true"}
        
        orgObj = session.query(cls.Organization).filter(cls.Organization.slack_teamid == json['slack_teamid']).filter(cls.Organization.token_name == json['token_name']).first()
        if orgObj:
            return {"tokenExist":"true"}
        
        
        #channelId = createChannel(json['channelName'])
        jsonStr = {"token_name":json['token_name'],
                    "slack_teamid":json['slack_teamid'],"a":json['a'],"b":json['b'],
                    "code":json['code'],"channelName":json['channelName'],"channelId":json['channelId']}
        organization = cls.Organization(jsonStr,session)
        organization.name = json['channelName']
        session.add(organization)
        session.flush()            
        usersDic = createUserAndUserOrganizations(organization.id,json['contributors'],json['token'],json['b'],json['access_token'])
        
        
        contribution = cls.Contribution()
        contribution.min_reputation_to_close = 0
        #contribution.file = 'Founding Contribution'
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
                contribution.ownerId = contributionContributor.contributor_id
            contribution.contributionContributors.append(contributionContributor)  
        userOrgObjectForOwner = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == contribution.ownerId).filter(cls.UserOrganization.organization_id == organization.id).first()
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
        jsonStr = {"tokens":json['token'],
                   "reputation":userOrgObjectForOwner.org_reputation,
                   "ownerId":contribution.ownerId,
                   "contribution_id":contribution.id,
                   "stake":userOrgObjectForOwner.org_reputation*5/100, 
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
                    for contributor in contributionObject.contributionContributors:
                        session.delete(contributor)
                    for bid in contributionObject.bids:
                        session.delete(bid)
                    session.delete(contributionObject)
                session.delete(userOrganization)        
            session.delete(orgObj)
            session.commit()
        return {}, 204
    
def getSlackUsers(access_token):
    print 'access_token'+access_token
    team_users_api_url = 'https://slack.com/api/users.list'
    headers = {'User-Agent': 'DEAP'}
    r = requests.get(team_users_api_url, params={'token':access_token}, headers=headers)
    users = json.loads(r.text)['members']
    print 'slack users:'+str(users)
    return users

    
class getAllSlackUsersResource(Resource):
    def post(self):
        print 'comes here'
        json = request.json
        access_token = json['access_token']
        userIds = json['userIds']
        searchString = json['searchString']
        
        users = getSlackUsers(access_token)
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
                if  searchString  not in realName and searchString  not in userName:
                    continue
            if len(userIdsList) > 0 :
                if slackUserId in userIdsList:   
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
        
        
    
def createUserAndUserOrganizations(organizaionId,contributors,token,b,access_token):
    
    usersInSystem = session.query(cls.User).all()
    contributionDic = {}
    for contributor in contributors :
        contributionDic[contributor['id']] = (float(token)/100)*float(contributor['percentage'])
    usersDic = {}
    for u in usersInSystem:
        usersDic[u.slackId] = u.id
    # parse response:
    users = getSlackUsers(access_token)
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
            jsonStr = {"name":user['name'],"slackId":user['id'],"url":user['profile']['image_48'],"url72":user['profile']['image_72'],"real_name":user['profile']['real_name']}
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
    milestones = [];
    user = session.query(cls.User).filter(cls.User.name == profile['user']).first()
    if not user:
        return []    
    bidsList = session.query(cls.Bid).filter(cls.Bid.ownerId == user.id).all()
    for bid in bidsList:        
        mileStoneObj = session.query(cls.MileStone).filter(cls.MileStone.contribution_id == bid.contribution_id).first()
        if mileStoneObj :
             milestones.append(mileStoneObj.id)
        else :
            contribitions.append(bid.contribution_id)
    
    jsonString = {'contribitions':contribitions,'milestones':milestones}
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
    



class MileStoneResource(Resource):
    @marshal_with(milestone_fields)
    def get(self, id):
        milestoneObject = session.query(cls.MileStone).filter(cls.MileStone.id == id).first()
        print 'got Get for MileStone fbid:'+id
        if not milestoneObject:
            abort(404, message="MileStone {} doesn't exist".format(id))
        userOrgObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == milestoneObject.userOrganization.organization_id).all()
        usersReputationDic = {}
        for userOrgObject in userOrgObjects:
            usersReputationDic[userOrgObject.user_id]=userOrgObject.org_reputation
        totalContributions = 0
        totalContributors = 0
        for milestoneContributor in milestoneObject.milestoneContributors:
            totalContributors = totalContributors + 1 
            milestoneContributor.name= getUser(milestoneContributor.contributor_id).name
            milestoneContributor.real_name= getUser(milestoneContributor.contributor_id).real_name
            milestoneContributor.url= getUser(milestoneContributor.contributor_id).url
        milestoneObject.current_org_id = milestoneObject.userOrganization.organization_id
        milestoneObject.channelName = milestoneObject.userOrganization.organization.channelName
        milestoneObject.code = milestoneObject.userOrganization.organization.code
        milestoneObject.tokenName = milestoneObject.userOrganization.organization.token_name
        for milestoneContribution in milestoneObject.milestoneContributions:
            countOfLines = 0
            shortDescription = '';
            milestoneContributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == milestoneContribution.contribution_id).first()
            if milestoneContributionObject.file != None :
                for line in milestoneContributionObject.file.splitlines():
                    countOfLines = countOfLines + 1
                    if(shortDescription != ''):
                        shortDescription = shortDescription  + '\n'
                    shortDescription = shortDescription + line
                    if countOfLines == 3 :
                        shortDescription = shortDescription + '....'
                        break    
            
                   
            totalContributions = totalContributions + 1 
            contributionContributorsObjs =milestoneContributionObject.contributionContributors
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
                contributionContributorsObj.url = getUser(contributionContributorsObj.contributor_id).url
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
        milestoneObject.contributions = totalContributions
        milestoneObject.contributors = totalContributors
        return milestoneObject

    def delete(self, id):
        milestoneObject = session.query(cls.MileStone).filter(cls.MileStone.id == id).first()
        if not milestoneObject:
            abort(404, message="MileStone {} doesn't exist".format(id))
        for milestoneContributor in milestoneObject.milestoneContributors:
            session.delete(milestoneContributor)
        for milestoneBid in milestoneObject.milestoneBids:
            session.delete(milestoneBid)
        for milestoneContribution in milestoneObject.milestoneContributions:
            session.delete(milestoneContribution)
        session.delete(milestoneObject)
        session.commit()
        return {}, 204
    
    @marshal_with(milestone_fields)   
    def post(self):          
        parsed_args = milestoneParser.parse_args()  
        milestone = cls.MileStone()
        milestone.description = parsed_args['description']
        milestone.title = parsed_args['title']
        milestone.users_organizations_id = parsed_args['users_organizations_id']
        milestone.destination_org_id = parsed_args['evaluatingTeam']
        session.add(milestone)
        session.flush()
        totalContributions = 0
        totalValue = 0
        totalTokens = 0            
        userOrgObjectForOwner = session.query(cls.UserOrganization).filter(cls.UserOrganization.id == parsed_args['users_organizations_id']).first()
        userOrgObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == userOrgObjectForOwner.organization_id).all()
        for userOrgObject in userOrgObjects:
            totalTokens = totalTokens + userOrgObject.org_tokens
            userOrgObject.org_tokens = 0
            session.add(userOrgObject)
            
        milestone.tokens = totalTokens
        allContributionObjects = session.query(cls.Contribution).filter(cls.Contribution.status == 'Open').filter(cls.Contribution.users_organizations_id == cls.UserOrganization.id).filter(cls.UserOrganization.organization_id == userOrgObjectForOwner.organization_id).all()
        contributorsDic = {}
        
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
            mileStoneContribution = cls.MileStoneContribution()
            contributionContributorsObjs = contribution.contributionContributors
            for contributionContributorsObj in contributionContributorsObjs:
                try:
                    contributorPercentage = contributorsDic[contributionContributorsObj.contributor_id]
                except KeyError:
                    contributorPercentage = 0
                contributorPercentage = contributorPercentage + contributionContributorsObj.percentage
                contributorsDic[contributionContributorsObj.contributor_id] = contributorPercentage
            mileStoneContribution.contribution_id = contribution.id
            mileStoneContribution.milestone_id = milestone.id
            
            milestone.milestoneContributions.append(mileStoneContribution) 
            contribution.status='Closed'
            session.add(contribution)
         
        milestone.contributions =  totalContributions
        milestone.totalValue =  totalValue
        perc = 0
        ownerId = ''
        for key, elem in contributorsDic.items():
            mileStoneContributor = cls.MileStoneContributor()
            mileStoneContributor.milestone_id = milestone.id
            mileStoneContributor.contributor_id = key
            mileStoneContributor.percentage = elem/totalContributions
            if float(mileStoneContributor.percentage) > perc:
                perc = float(mileStoneContributor.percentage)
                ownerId = mileStoneContributor.contributor_id
            milestone.milestoneContributors.append(mileStoneContributor)
        userOrgObjectForTargetOwner = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == ownerId).filter(cls.UserOrganization.organization_id == parsed_args['evaluatingTeam']).first()
        contribution = cls.Contribution()
        contribution.ownerId = ownerId
        milestone.ownerId = ownerId
        contribution.min_reputation_to_close = 0
        contribution.file = parsed_args['description']
        contribution.title = parsed_args['title']
        contribution.users_organizations_id = userOrgObjectForTargetOwner.id
        session.add(contribution)
        session.flush()
        for contributor in milestone.milestoneContributors:             
            contributionContributor = cls.ContributionContributor()
            contributionContributor.contributor_id = contributor.contributor_id
            contributionContributor.contribution_id=contribution.id
            contributionContributor.percentage=contributor.percentage
            contribution.contributionContributors.append(contributionContributor)  
        
        session.add(contribution)
        milestone.contribution_id =  contribution.id 
        
        userOrgObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == parsed_args['evaluatingTeam']).all()
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
          
        return milestone, 201

    
    
    
class OrganizationCurrentStatusResource(Resource):
    @marshal_with(milestone_fields)
    def get(self, orgId):
        milestone = cls.MileStone()
        totalTokens = 0
        userOrgObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == orgId).all()
        usersReputationDic = {}
        orgObject = session.query(cls.Organization).filter(cls.Organization.id == orgId).first()
        for userOrgObject in userOrgObjects:
            totalTokens = totalTokens + userOrgObject.org_tokens
            usersReputationDic[userOrgObject.user_id]=userOrgObject.org_reputation
        milestone.tokens = totalTokens
        milestone.code = orgObject.code
        milestone.tokenName = orgObject.token_name
        milestone.channelName = orgObject.channelName
        allContributionObjects = session.query(cls.Contribution).filter(cls.Contribution.status == 'Open').filter(cls.Contribution.users_organizations_id == cls.UserOrganization.id).filter(cls.UserOrganization.organization_id == orgId).all()
        contributorsDic = {}
        totalContributions = 0
        totalContributors = 0
        totalValue = 0
        for contribution in allContributionObjects:
            shortDescription = ''
            countOfLines = 0
            if contribution.file != None :
                for line in contribution.file.splitlines():
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
            mileStoneContribution = cls.MileStoneContribution()
            mileStoneContribution.valuation = currentValuation
            mileStoneContribution.description = shortDescription
            contributionContributorsObjs = contribution.contributionContributors
            finalCountOfContributors = 0
            for contributionContributorsObj in contributionContributorsObjs:
                finalCountOfContributors = finalCountOfContributors + 1
                contributionContributorsObj.reputation = usersReputationDic[contributionContributorsObj.contributor_id]
                try:
                    contributorPercentage = contributorsDic[contributionContributorsObj.contributor_id]
                except KeyError:
                    contributorPercentage = 0
                contributorPercentage = contributorPercentage + contributionContributorsObj.percentage
                contributorsDic[contributionContributorsObj.contributor_id] = contributorPercentage
            contributionContributorsObjs.sort(key=lambda x: x.reputation, reverse=True)
            totalCountOfContrbutors = 0
            mileStoneContribution.contributors = []
            for contributionContributorsObj in contributionContributorsObjs:
                totalCountOfContrbutors = totalCountOfContrbutors +1
                contributionContributorsObj.memberId = getUser(contributionContributorsObj.contributor_id).slackId
                contributionContributorsObj.url = getUser(contributionContributorsObj.contributor_id).url
                mileStoneContribution.contributors.append(contributionContributorsObj)
                print 'contributionContributorsObj.reputation'+str(contributionContributorsObj.reputation)
                if totalCountOfContrbutors == 8 :
                    break
            mileStoneContribution.remainingContributors = finalCountOfContributors - totalCountOfContrbutors
            mileStoneContribution.contribution_id = contribution.id
            mileStoneContribution.title= contribution.title
            mileStoneContribution.date= contribution.time_created.date()
            milestone.milestoneContributions.append(mileStoneContribution) 
         
        milestone.contributions =  totalContributions
        milestone.totalValue =  totalValue
        for key, elem in contributorsDic.items():
            totalContributors = totalContributors + 1
            mileStoneContributor = cls.MileStoneContributor()
            mileStoneContributor.id = key
            mileStoneContributor.percentage = elem/totalContributions
            mileStoneContributor.name= getUser(mileStoneContributor.id).name
            mileStoneContributor.real_name= getUser(mileStoneContributor.id).real_name
            mileStoneContributor.url= getUser(mileStoneContributor.id).url
            milestone.milestoneContributors.append(mileStoneContributor)
        milestone.contributors = totalContributors
        return milestone


class AllMileStonesForOrgResource(Resource):
    def get(self, id):
        allMileStoneObjects = session.query(cls.MileStone).filter(cls.MileStone.users_organizations_id == cls.UserOrganization.id).filter(cls.UserOrganization.organization_id == id).all()
        mileStonesJson = []
        for milestone in allMileStoneObjects:
            jsonStr = {"id":milestone.id,"title":milestone.title}
            mileStonesJson.append(jsonStr)
        return mileStonesJson