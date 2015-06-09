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
    schema.Column('slack_id', types.Unicode(255)),
    schema.Column('tokens', types.Integer),
    schema.Column('reputation',  types.Integer),
)

"""
Bid - schema definition:
"""
bid_table = schema.Table('bid', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('bid_seq_id', optional=True), primary_key=True),
    schema.Column('owner', types.Integer,
        schema.ForeignKey('user.id')),   
    schema.Column('contribution_id', types.Integer,
        schema.ForeignKey('contribution.id')),
    schema.Column('tokens', types.Integer),
    schema.Column('stake', types.Integer),
    schema.Column('reputation',  types.Integer),
    schema.Column('current_rep_to_return', types.Integer),
    schema.Column('contribution_value_after_bid',  types.Integer),
)


"""
Contribution - schema definition:
"""
contribution_table = schema.Table('contribution', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('contribution_seq_id', optional=True), primary_key=True),
    schema.Column('owner', types.Integer,
        schema.ForeignKey('user.id')),
    schema.Column('min_reputation_to_close',  types.Integer,nullable=True),
    schema.Column('time_created', types.DateTime(), default=now),
    schema.Column('file', types.Text()),
    schema.Column('title', types.Text()),
    schema.Column('status', types.String,default='Open'),
)

"""
Contribution Contributers List - schema definition:
"""
contribution_contributer_table = schema.Table('contribution_contributer', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('contribution_contributer_seq_id', optional=True), primary_key=True),
    schema.Column('contribution_id', types.Integer,
        schema.ForeignKey('contribution.id')),
    schema.Column('contributer_id', types.Integer,
        schema.ForeignKey('user.id')),
    schema.Column('contributer_percentage', types.INTEGER),   
)


"""
Relationships - definitions
"""
orm.mapper(cls.User, user_table, properties={

})

orm.mapper(cls.Contribution, contribution_table, properties={
    'contribution_owner':orm.relation(cls.User, backref='contribution'),
    'bids':orm.relation(cls.Bid, backref='contribution'),  
    'contributionContributers':orm.relation(cls.ContributionContributer, backref='contribution'),                                                  
})

orm.mapper(cls.ContributionContributer, contribution_contributer_table, properties={
    'contribution_user':orm.relation(cls.User, backref='contributer'),                                                
})


orm.mapper(cls.Bid, bid_table, properties={
    'bid_owner':orm.relation(cls.User, backref='bid'),	
})



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