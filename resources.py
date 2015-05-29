
from db import session
import classes as cls
#import modules.SparkWorldEng.main as worldEng
import modules.taskDispatcher as dispatcher

from flask.ext.restful import reqparse
from flask.ext.restful import abort
from flask.ext.restful import Resource
from flask.ext.restful import fields
from flask.ext.restful import marshal_with
import json  

parser = reqparse.RequestParser()

parser.add_argument('userId', type=str)

user_fields = {
    'id': fields.Integer,
    'name': fields.String,
}

bid_fields = {
    'id': fields.Integer,
}

parser.add_argument('name', type=str)
parser.add_argument('slackId', type=str)    
class UserResource(Resource):
    @marshal_with(user_fields)
    def get(self, id):
        char = session.query(cls.User).filter(cls.User.slackId == id).first()
        print 'got Get for User fbid:'+id
        if not char:
            abort(404, message="User {} doesn't exist".format(id))
        return char   
    
    def delete(self, id):
        char = session.query(cls.User).filter(cls.User.id == id).first()
        if not char:
            abort(404, message="User {} doesn't exist".format(id))
        session.delete(char)
        session.commit()
        return {}, 204

    @marshal_with(user_fields)
    def put(self, id):
        parsed_args = parser.parse_args()
        char = session.query(cls.User).filter(cls.User.id == id).first()
        session.add(char)
        session.commit()
        return char, 201

    @marshal_with(user_fields)
    def post(self):
        parsed_args = parser.parse_args()

        jsonStr = {"slackId":parsed_args['slackId'],
                    "name":parsed_args['name']}
        user = cls.User(jsonStr,session)

        session.add(user)
        session.commit()
        return user, 201
        


parser.add_argument('tokens', type=str)
parser.add_argument('reputation', type=str)	
parser.add_argument('ownerId', type=str)
parser.add_argument('contributionId', type=str)
class BidResource(Resource):
    @marshal_with(bid_fields)
    def get(self, id):
        char = session.query(cls.Bid).filter(cls.Bid.id == id).first()
        print 'got Get for User fbid:'+id
        if not char:
            abort(404, message="User {} doesn't exist".format(id))
        return char

    def delete(self, id):
        char = session.query(cls.Bid).filter(cls.Bid.id == id).first()
        if not char:
            abort(404, message="User {} doesn't exist".format(id))
        session.delete(char)
        session.commit()
        return {}, 204

    @marshal_with(bid_fields)
    def put(self, id):
        parsed_args = parser.parse_args()
        char = session.query(cls.Bid).filter(cls.Bid.id == id).first()
        session.add(char)
        session.commit()
        return char, 201

    @marshal_with(bid_fields)
    def post(self):
        parsed_args = parser.parse_args()

        jsonStr = {"tokens":parsed_args['tokens'],
                   "reputation":parsed_args['reputation'],
                   "owner":parsed_args['ownerId'],
                   "contribution_id":parsed_args['contributionId']
                    }
                    
        # TBD: create resource if doesnt exist and add to it the new bid:
        bid = cls.Bid(jsonStr,session)

        session.add(bid)
        session.commit()
        return bid, 201