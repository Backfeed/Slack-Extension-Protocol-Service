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
    schema.Column('slackId', types.Unicode(255)),
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
    schema.Column('resourceid', types.Integer,
        schema.ForeignKey('resource.id')),
    schema.Column('tokens', types.Integer),
    schema.Column('reputation',  types.Integer),
)

"""
Resource - schema definition:
"""
resource_table = schema.Table('resource', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('resource_seq_id', optional=True), primary_key=True),
    schema.Column('owner', types.Integer,
        schema.ForeignKey('user.id')),
    schema.Column('content', types.Text()),
    schema.Column('resource_id', types.Unicode(255)),
)

"""
Relationships - definitions
"""
orm.mapper(cls.User, user_table, properties={
    'character':orm.relation(cls.Character, backref='user'),
	'tasks':orm.relation(cls.UserTask, backref='user'),

})

orm.mapper(cls.Resource, resource_table, properties={
    'res_owner':orm.relation(cls.User, backref='resource'),
	'bids':orm.relation(cls.Bid),

})

orm.mapper(cls.Bid, bid_table, properties={
    'bid_owner':orm.relation(cls.User, backref='bid'),
	'resource':orm.relation(cls.Resource),

})

"""
Relationships - definitions
"""
orm.mapper(cls.Monster, monster_table)

# define the relation between town -> events:
orm.mapper(cls.Town, town_table, properties={
    'events':orm.relation(cls.Event, backref='town'),
	'tasks':orm.relation(cls.LocationTask, backref='town'),

    'monsters':orm.relation(cls.Monster, secondary=townmonster_table,backref="towns"),

})

orm.mapper(cls.Event, event_table)
orm.mapper(cls.LocationTask, location_task_table)
orm.mapper(cls.Log, log_table)

"""
Character -> User
"""
# define the relation between User -> character:
orm.mapper(cls.User, user_table, properties={
    'character':orm.relation(cls.Character, backref='user'),
	'tasks':orm.relation(cls.UserTask, backref='user'),

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