from sqlalchemy import orm
import datetime
from sqlalchemy import schema, types
import classes as cls

metadata = schema.MetaData()


def now():
    return datetime.datetime.now()

"""
Tables - schema definition:
"""

"""
User - schema definition:
"""
user_table = schema.Table('user', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('user_seq_id', optional=True), primary_key=True),

    schema.Column('name', types.Unicode(255)),
    schema.Column('real_name', types.Unicode(255)),
    schema.Column('url', types.Unicode(255)),
    schema.Column('url72', types.Unicode(255)),
    schema.Column('slackId', types.Unicode(255)),
)

"""
Bid - schema definition:
"""
bid_table = schema.Table('bid', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('bid_seq_id', optional=True), primary_key=True),
    schema.Column('ownerId', types.Integer,
        schema.ForeignKey('user.id')),   
    schema.Column('contribution_id', types.Integer,
        schema.ForeignKey('contribution.id')),
    schema.Column('tokens', types.Float),
    schema.Column('stake', types.Float),
    schema.Column('reputation',  types.Float),
    schema.Column('current_rep_to_return', types.Float),
    schema.Column('weight', types.Float),
    schema.Column('contribution_value_after_bid',  types.Float),
    schema.Column('time_created', types.DateTime(), default=now),

)


"""
Contribution - schema definition:
"""
contribution_table = schema.Table('contribution', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('contribution_seq_id', optional=True), primary_key=True),
    schema.Column('ownerId', types.Integer,
        schema.ForeignKey('user.id')),
    schema.Column('users_organizations_id', types.Integer,
        schema.ForeignKey('users_organizations.id')),
    schema.Column('min_reputation_to_close',  types.Integer,nullable=True),
    schema.Column('time_created', types.DateTime(), default=now),
    schema.Column('file', types.Text()),
    schema.Column('title', types.Text()),
    schema.Column('status', types.String(100),default='Open'),
    schema.Column('currentValuation',  types.Float,default=0),
    schema.Column('valueIndic',  types.Integer,default=0),
)

"""
Contribution Contributors List - schema definition:
"""
contribution_contributor_table = schema.Table('contribution_contributor', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('contribution_contributor_seq_id', optional=True), primary_key=True),
    schema.Column('contribution_id', types.Integer,
        schema.ForeignKey('contribution.id')),
    schema.Column('contributor_id', types.Integer,
        schema.ForeignKey('user.id')),
    schema.Column('percentage', types.FLOAT),   
)

"""
MileStone Bid - schema definition:
"""
milestone_bid_table = schema.Table('milestone_bid', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('milestone_bid_seq_id', optional=True), primary_key=True),
    schema.Column('ownerId', types.Integer,
        schema.ForeignKey('user.id')),   
    schema.Column('milestone_id', types.Integer,
        schema.ForeignKey('milestone.id')),
    schema.Column('tokens', types.Float),
    schema.Column('stake', types.Float),
    schema.Column('reputation',  types.Float),
    schema.Column('current_rep_to_return', types.Float),
    schema.Column('weight', types.Float),
    schema.Column('milestone_value_after_bid',  types.Float),
    schema.Column('time_created', types.DateTime(), default=now),

)


"""
MileStone - schema definition:
"""
milestone_table = schema.Table('milestone', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('milestone_seq_id', optional=True), primary_key=True),
    schema.Column('ownerId', types.Integer,
        schema.ForeignKey('user.id')),
    schema.Column('users_organizations_id', types.Integer,
        schema.ForeignKey('users_organizations.id')),
    schema.Column('contribution_id', types.Integer),
    schema.Column('start_date', types.DateTime(), default=now),
    schema.Column('end_date', types.DateTime(), default=now),
    schema.Column('description', types.Text()),
    schema.Column('title', types.Text()),
    schema.Column('tokens',  types.Float),
    schema.Column('totalValue',  types.Float),
    schema.Column('destination_org_id', types.Integer),
    schema.Column('contributions',  types.Integer),
)

"""
MileStone Contributors List - schema definition:
"""
milestone_contributor_table = schema.Table('milestone_contributor', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('milestone_contributor_seq_id', optional=True), primary_key=True),
    schema.Column('milestone_id', types.Integer,
        schema.ForeignKey('milestone.id')),
    schema.Column('contributor_id', types.Integer,
        schema.ForeignKey('user.id')),
    schema.Column('percentage', types.FLOAT),   
)

"""
MileStone Contribution List - schema definition:
"""
milestone_contribution_table = schema.Table('milestone_contribution', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('milestone_contribution_seq_id', optional=True), primary_key=True),
    schema.Column('milestone_id', types.Integer,
        schema.ForeignKey('milestone.id')),
    schema.Column('contribution_id', types.Integer,
        schema.ForeignKey('contribution.id')),
)

"""
Organization - schema definition:
"""
organization_table = schema.Table('organization', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('organization_seq_id', optional=True), primary_key=True),

    schema.Column('token_name', types.Unicode(255),nullable=False),
    schema.Column('slack_teamid', types.Unicode(255)),
    schema.Column('name', types.Unicode(255),nullable=False),
    schema.Column('code', types.Unicode(255),nullable=False),
    schema.Column('channelName', types.Unicode(255),nullable=False),
    schema.Column('channelId', types.Unicode(255),nullable=False),
    schema.Column('reserveTokens', types.Float),
    schema.Column('a', types.Integer),
    schema.Column('b', types.Integer),
)

"""
User Organizations - schema definition:
"""
users_organizations_table = schema.Table('users_organizations', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('users_organizations_seq_id', optional=True), primary_key=True),
    schema.Column('user_id', types.Integer,
        schema.ForeignKey('user.id')),
    schema.Column('organization_id', types.Integer,
        schema.ForeignKey('organization.id')),
    schema.Column('org_tokens', types.Float),
    schema.Column('org_reputation',  types.Float),   
)


"""
Contribution value- schema definition:
"""
contribution_value_table = schema.Table('contributionValue', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('contribution_value_seq_id', optional=True), primary_key=True),
    schema.Column('user_id', types.Integer,
        schema.ForeignKey('user.id')),
    schema.Column('users_organizations_id', types.Integer,
        schema.ForeignKey('users_organizations.id')),
    schema.Column('contribution_id', types.Integer,
        schema.ForeignKey('contribution.id')),
    schema.Column('reputationGain',  types.Float,default=0),
    schema.Column('reputation',  types.Float,default=0),
)

"""
Relationships - definitions
"""
orm.mapper(cls.User, user_table, properties={
    'userOrganizations':orm.relation(cls.UserOrganization, backref='user'),
})

orm.mapper(cls.UserOrganization, users_organizations_table, properties={
          'contributions':orm.relation(cls.Contribution),                                                              
                                                                        })


orm.mapper(cls.MileStone, milestone_table, properties={
    'milestone_owner':orm.relation(cls.User, backref='milestone'),
    'milestoneBids':orm.relation(cls.MileStoneBid, backref='milestone'),  
    'milestoneContributors':orm.relation(cls.MileStoneContributor, backref='milestone'),  
    'milestoneContributions':orm.relation(cls.MileStoneContribution, backref='milestone'),                                                  
    'userOrganization':orm.relation(cls.UserOrganization),
})

orm.mapper(cls.Contribution, contribution_table, properties={
    'contribution_owner':orm.relation(cls.User, backref='contribution'),
    'bids':orm.relation(cls.Bid, backref='contribution'),  
    'contributionContributors':orm.relation(cls.ContributionContributor, backref='contribution'),                                                  
    'userOrganization':orm.relation(cls.UserOrganization),
})

orm.mapper(cls.ContributionContributor, contribution_contributor_table, properties={
    'contribution_user':orm.relation(cls.User, backref='contributor'),                                                
})

orm.mapper(cls.MileStoneContributor, milestone_contributor_table, properties={
    'milestone_user':orm.relation(cls.User, backref='milestoneContributor'),                                                
})

orm.mapper(cls.MileStoneContribution, milestone_contribution_table, properties={
    'milestone_contribution':orm.relation(cls.Contribution, backref='milestoneContribution'),                                                
})


orm.mapper(cls.Bid, bid_table, properties={
    'bid_owner':orm.relation(cls.User, backref='bid'),    
})

orm.mapper(cls.MileStoneBid, milestone_bid_table, properties={
    'milestone_bid_owner':orm.relation(cls.User, backref='milestoneBid'),    
})

orm.mapper(cls.Organization, organization_table, properties={
    'userOrganizations':orm.relation(cls.UserOrganization, backref='organization'),                                                  
})

orm.mapper(cls.ContributionValue, contribution_value_table)

"""
# BELOW is an example of relations between objects, (for when you dont have just a simple object that holds data)
# in this example we see "comments", and "tags" tables which have an additional column  which relates back  to a "page" object. 

page_table = schema.Table('page', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('page_seq_id', optional=True), primary_key=True),
    schema.Column('content', types.Text(), nullable=False),
    schema.Column('posted', types.DateTime(), default=now),
    schema.Column('title', types.Unicode(255), default=u'Untitled Page'),
    schema.Column('heading', types.Unicode(255)),
)
comment_table = schema.Table('comment', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('comment_seq_id', optional=True), primary_key=True),
    schema.Column('pageid', types.Integer,
        schema.ForeignKey('page.id'), nullable=False),
    schema.Column('content', types.Text(), default=u''),
    schema.Column('name', types.Unicode(255)),
    schema.Column('email', types.Unicode(255), nullable=False),
    schema.Column('created', types.TIMESTAMP(), default=now()),
)
pagetag_table = schema.Table('pagetag', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('pagetag_seq_id', optional=True), primary_key=True),
    schema.Column('pageid', types.Integer, schema.ForeignKey('page.id')),
    schema.Column('tagid', types.Integer, schema.ForeignKey('tag.id')),
)
tag_table = schema.Table('tag', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('tag_seq_id', optional=True), primary_key=True),
    schema.Column('name', types.Unicode(20), nullable=False, unique=True),
)

class Page(object):
    pass

class Comment(object):
    pass

class Tag(object):
    pass

orm.mapper(Page, page_table, properties={
    'comments':orm.relation(Comment, backref='page'),
    'tags':orm.relation(Tag, secondary=pagetag_table)
})
orm.mapper(Comment, comment_table)
orm.mapper(Tag, tag_table)
"""