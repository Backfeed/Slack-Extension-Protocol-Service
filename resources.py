from db import session
import classes as cls

from flask.ext.restful import reqparse
from flask.ext.restful import abort
from flask.ext.restful import fields
from flask.ext.restful import marshal_with
import json
from auth import login_required
import requests
from flask import g

import vdp
from datetime import datetime

#from flask.ext.restful import Resource
#Add Authentication required to all resources:
from flask.ext.restful import Resource as FlaskResource
class Resource(FlaskResource):
   method_decorators = [login_required]   # applies to all inherited resources

userParser = reqparse.RequestParser()
organizationParser = reqparse.RequestParser()
userOrganizationParser = reqparse.RequestParser()
contributionParser = reqparse.RequestParser()
bidParser = reqparse.RequestParser()
closeContributionParser = reqparse.RequestParser()

contributionParser.add_argument('contributers', type=cls.Contributer, action='append')
contributionParser.add_argument('intialBid', type=cls.IntialBid)
contributionParser.add_argument('owner', type=int,required=True)
contributionParser.add_argument('users_organizations_id', type=int,required=True)
contributionParser.add_argument('min_reputation_to_close', type=str)
contributionParser.add_argument('file', type=str,required=True)
contributionParser.add_argument('title', type=str)

userParser.add_argument('userId', type=str)
userParser.add_argument('name', type=str,required=True)
userParser.add_argument('slack_id', type=str)

organizationParser.add_argument('token_name', type=str)
organizationParser.add_argument('slack_teamid', type=str,required=True)
organizationParser.add_argument('intial_tokens', type=str)
organizationParser.add_argument('name', type=str)


bidParser.add_argument('tokens', type=str,required=True)
bidParser.add_argument('reputation', type=str,required=True)    
bidParser.add_argument('contribution_id', type=str,required=True)
bidParser.add_argument('owner', type=int,required=True)

closeContributionParser.add_argument('owner', type=int,required=True)
closeContributionParser.add_argument('id', type=int,required=True)

user_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'slack_id': fields.String,    
}

userOrganization_fields = {
    'id': fields.Integer,
    'user_id': fields.String,
    'organization_id': fields.String,
    'org_tokens': fields.String,
    'org_reputation': fields.String
}

bid_fields = {
    'id': fields.Integer,
    'contribution_id': fields.Integer
}

bid_nested_fields = {}
bid_nested_fields['tokens'] = fields.String
bid_nested_fields['reputation'] = fields.String
bid_nested_fields['owner'] = fields.Integer

contributer_nested_fields = {}
contributer_nested_fields['contributer_id'] = fields.String
contributer_nested_fields['contributer_percentage'] = fields.String
contributer_nested_fields['name'] = fields.String

contribution_fields = {}
contribution_fields['id'] = fields.Integer
contribution_fields['time_created'] = fields.DateTime
contribution_fields['users_organizations_id'] = fields.Integer
contribution_fields['status'] = fields.String
contribution_fields['owner'] = fields.String
contribution_fields['file'] = fields.String
contribution_fields['title'] = fields.String
contribution_fields['bids'] = fields.Nested(bid_nested_fields)
contribution_fields['contributionContributers'] = fields.Nested(contributer_nested_fields)

contribution_status_fields ={}
contribution_status_fields['currentValuation'] = fields.Integer
contribution_status_fields['totalReputaion'] = fields.Integer
contribution_status_fields['myValuation'] = fields.Integer
contribution_status_fields['myReputaion'] = fields.Integer


def getUser(id):
    user = session.query(cls.User).filter(cls.User.id == id).first()
    return user
   
class UserResource(Resource):
    @marshal_with(user_fields)
    def get(self, id):
        char = getUser(id)
        print 'got Get for User fbid:'+id
        if not char:
            abort(404, message="User {} doesn't exist".format(id))
        return char   
    
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

        jsonStr = {"slack_id":parsed_args['slack_id'],
                    "name":parsed_args['name']
                    }
        user = cls.User(jsonStr,session)

        session.add(user)
        session.commit()
        return user, 201
    
class AllUserResource(Resource):
    @marshal_with(user_fields)
    def get(self,organizationId):
        users =[]    
        userOrganizationObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == organizationId).all()
        for userOrganization in userOrganizationObjects :
            users.append(userOrganization.user )           
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
                   "stake":10, # TBD: parse stake
                   "time_created":datetime.now()
                    }

        bid = cls.Bid(jsonStr,session)                       
        #session.add(bid);
        #session.commit();
        # process contribution:
        bid = vdp.process_bid(bid)
        if( not bid ):
            abort(404, message="Failed to process bid".format(contributionid))

        return bid, 201

class ContributionResource(Resource):
    @marshal_with(contribution_fields)
    def get(self, id):
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        print 'got Get for Contribution fbid:'+id
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(id))
        for contributer in contributionObject.contributionContributers:
            contributer.name= getUser(contributer.contributer_id).name
        return contributionObject

    def delete(self, id):
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(id))
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
        userObj = getUser(contribution.owner)        
        if not userObj:
            abort(404, message="User who is creating contribution {} doesn't exist".format(contribution.owner))        
        for contributer in parsed_args['contributers']:             
            contributionContributer = cls.ContributionContributer()
            contributionContributer.contributer_id = contributer.obj1['contributer_id']
            if contributionContributer.contributer_id == '':
                continue
            userObj = getUser(contributionContributer.contributer_id)        
            if not userObj:
                abort(404, message="Contributer {} doesn't exist".format(contributionContributer.contributer_id))
            contributionContributer.contribution_id=contribution.id
            contributionContributer.contributer_percentage=contributer.obj1['contributer_percentage']
            contribution.contributionContributers.append(contributionContributer)  
        if(len(contribution.contributionContributers) == 0):
            contributionContributer = cls.ContributionContributer()
            contributionContributer.contributer_id = contribution.owner
            contributionContributer.contributer_percentage = '100'
            contribution.contributionContributers.append(contributionContributer)  
        if((parsed_args['intialBid'].obj1['tokens'] != '') & (parsed_args['intialBid'].obj1['reputation'] != '')):      
                jsonStr = {"tokens":parsed_args['intialBid'].obj1['tokens'],
                   "reputation":parsed_args['intialBid'].obj1['reputation'],
                   "owner":contribution.owner,
                   "contribution_id":contribution.id
                    }
                intialBidObj = cls.Bid(jsonStr,session)        
                contribution.bids.append(intialBidObj)
        session.add(contribution)
        session.commit()        
       
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
        contributionObject = session.query(cls.Contribution).filter(cls.UserOrganization.organization_id == organizationId).all()
        return contributionObject
    
class ContributionStatusResource(Resource):
    @marshal_with(contribution_status_fields)
    def get(self,id,userId):
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        print 'got Get for Contribution fbid:'+id
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(id))
        currentValuation = 0
        totalReputaion = 0
        myValuation = 0
        myReputaion = 0
        for bid in contributionObject.bids:
            totalReputaion = totalReputaion + bid.reputation
            if(str(bid.owner) == str(userId)):
                myReputaion = myReputaion + bid.reputation 
                myValuation = myValuation + bid.tokens
        jsonStr = {"currentValuation":currentValuation,
                   "totalReputaion":totalReputaion,
                   "myValuation":myValuation,
                   "myReputaion":myReputaion
                    }
        return jsonStr
    
    
class OrganizationResource(Resource):
    
    @marshal_with(userOrganization_fields)
    def post(self):
        parsed_args = organizationParser.parse_args()

        jsonStr = {"token_name":parsed_args['token_name'],
                    "slack_teamid":parsed_args['slack_teamid'],
                    "intial_tokens":parsed_args['intial_tokens'],
                    "name":parsed_args['name']
                    }
        organization = cls.Organization(jsonStr,session)

        session.add(organization)
        session.flush()
        createUserAndUserOrganizations(organization.id)
        session.commit()
        userOrgObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == g.user_id).first()
        return userOrgObj, 201
    
def createUserAndUserOrganizations(organizaionId):
    team_users_api_url = 'https://slack.com/api/users.list'
    headers = {'User-Agent': 'DEAP'}
    r = requests.get(team_users_api_url, params={'token':g.access_token}, headers=headers)
    # parse response:
    users = json.loads(r.text)['members']
    print 'slack users:'+str(users)
    for user in users :
        userId =g.user_id
        if(user['id'] != g.slackUserId):
            jsonStr = {"slack_id":user['id'],"name":user['name']}
            u = cls.User(jsonStr,session)
            session.add(u) 
            session.flush() 
            userId = u.id
                       
        jsonStr = {"user_id":userId,
                    "organization_id":organizaionId,
                    "org_tokens":100,
                    "org_reputation":100
                    }
        userOrganization = cls.UserOrganization(jsonStr,session)
        session.add(userOrganization)    
    
