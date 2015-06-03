
from db import session
import classes as cls
#import modules.SparkWorldEng.main as worldEng

from flask.ext.restful import reqparse
from flask.ext.restful import abort
from flask.ext.restful import Resource
from flask.ext.restful import fields
from flask.ext.restful import marshal_with
import json

userParser = reqparse.RequestParser()
contributionParser = reqparse.RequestParser()
bidParser = reqparse.RequestParser()
closeContributionParser = reqparse.RequestParser()

contributionParser.add_argument('contributers', type=cls.Contributer, action='append')
contributionParser.add_argument('intialBid', type=cls.IntialBid,required=True)
contributionParser.add_argument('owner', type=int,required=True)
contributionParser.add_argument('min_reputation_to_close', type=int)
contributionParser.add_argument('file', type=str,required=True)

userParser.add_argument('userId', type=str)
userParser.add_argument('name', type=str,required=True)
userParser.add_argument('slackId', type=str)

bidParser.add_argument('tokens', type=str,required=True)
bidParser.add_argument('reputation', type=str,required=True)    
bidParser.add_argument('contribution_id', type=str,required=True)
bidParser.add_argument('owner', type=int,required=True)

closeContributionParser.add_argument('owner', type=int,required=True)

user_fields = {
    'id': fields.Integer,
    'name': fields.String,
}

bid_fields = {
    'id': fields.Integer,
    'contribution_id': fields.Integer,
}

contribution_fields = {
    'id': fields.Integer,
    'status':fields.String,
    'file':fields.String,
}

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

        jsonStr = {"slack_id":parsed_args['slackId'],
                    "name":parsed_args['name']}
        user = cls.User(jsonStr,session)

        session.add(user)
        session.commit()
        return user, 201
        
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
                   "contribution_id":parsed_args['contribution_id']
                    }
        bid = cls.Bid(jsonStr,session)                       
        session.add(bid)
        session.commit()
        return bid, 201
    

class ContributionResource(Resource):
    @marshal_with(contribution_fields)
    def get(self, id):
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        print 'got Get for Contribution fbid:'+id
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(id))
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
        userObj = getUser(contribution.owner)        
        if not userObj:
            abort(404, message="User who is creating contribution {} doesn't exist".format(contribution.owner))        
        for contributer in parsed_args['contributers']:             
            contributionContributer = cls.ContributionContributer()
            contributionContributer.contributer_id = contributer.obj1['contributer_id']
            userObj = getUser(contributionContributer.contributer_id)        
            if not userObj:
                abort(404, message="Contributer {} doesn't exist".format(contributionContributer.contributer_id))
            contributionContributer.contribution_id=contribution.id
            contributionContributer.contributer_percentage=contributer.obj1['contributer_percentage']
            contribution.contributionContributers.append(contributionContributer)        
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
    def post(self,id):      
        parsed_args = closeContributionParser.parse_args()   
        ownerId = parsed_args['owner'] 
        userObj = getUser(ownerId)  
        if not userObj:
            abort(404, message="User who is closing contribution {} doesn't exist".format(ownerId)) 
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(id))
        if contributionObject.status != 'Open':
            abort(404, message="Contribution {} is already closed".format(id))        
        if userObj.id != contributionObject.owner:
            abort(404, message="Only contribution owner can close this contribution".format(ownerId)) 
        contributionObject.status='Closed'
        session.add(contributionObject)
        session.commit()        
       
        return contributionObject, 201