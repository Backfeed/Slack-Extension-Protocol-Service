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
Agent - schema definition:
"""
agent_table = schema.Table('agent', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('agent_seq_id', optional=True), primary_key=True),

    schema.Column('name', types.Unicode(255)),
    schema.Column('password', types.Unicode(255)),
    schema.Column('fullName', types.Unicode(255)),
    schema.Column('imgUrl', types.Unicode(255)),
)


agent_handle_table = schema.Table('agent_handle', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('agent_seq_id', optional=True), primary_key=True),

    schema.Column('agentId', types.Integer,
        schema.ForeignKey('agent.id'),nullable=False),
    schema.Column('handleName', types.Unicode(255)),
    schema.Column('handleType', types.Unicode(255)),
)

"""
Group - schema definition:
"""
group_table = schema.Table('group', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('group_seq_id', optional=True), primary_key=True),
    schema.Column('agentId', types.Integer,
        schema.ForeignKey('agent.id'),nullable=False),                              
    schema.Column('name', types.Unicode(255),nullable=False),
    schema.Column('description', types.Unicode(255)),
    schema.Column('protocol', types.Unicode(255),nullable=False),
)

"""
Agent groups - schema definition:
"""
agent_group_table = schema.Table('agent_group', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('agent_group_seq_id', optional=True), primary_key=True),
    schema.Column('agentId', types.Integer,
        schema.ForeignKey('agent.id')),
    schema.Column('groupId', types.Integer,
        schema.ForeignKey('group.id')),
)


"""
Network - schema definition:
"""
network_table = schema.Table('network', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('network_seq_id', optional=True), primary_key=True),
    schema.Column('agentId', types.Integer,
        schema.ForeignKey('agent.id'),nullable=False),
    schema.Column('groupId', types.Integer,
        schema.ForeignKey('group.id'),nullable=False),
    schema.Column('protocol',types.Unicode(2000)),
    schema.Column('tokenName', types.Unicode(60)),
    schema.Column('name', types.Unicode(255),nullable=False),
    schema.Column('description', types.Unicode(255),nullable=False),
    schema.Column('tokenSymbol', types.Unicode(3)),
    schema.Column('tokenTotal', types.Integer),
    schema.Column('comment', types.Unicode(2000)),
    schema.Column('status', types.Unicode(100),default=u'Open'),
    schema.Column('similarEvaluationRate', types.Integer),
    schema.Column('passingResponsibilityRate', types.Integer),
)

"""
Agent networks - schema definition:
"""
agent_network_table = schema.Table('agent_network', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('agent_network_seq_id', optional=True), primary_key=True),
    schema.Column('agentId', types.Integer,
        schema.ForeignKey('agent.id')),
    schema.Column('networkId', types.Integer,
        schema.ForeignKey('network.id')),
    schema.Column('tokens', types.Float),
    schema.Column('reputation',  types.Float),   
)

"""
network hanldes - schema definition:
"""
network_handle_table = schema.Table('network_handle', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('network_handle_seq_id', optional=True), primary_key=True),
    schema.Column('networkId', types.Integer,
        schema.ForeignKey('network.id')),
    schema.Column('handleName', types.Unicode(255)),
    schema.Column('handleType', types.Unicode(255)),   
)




"""
Contribution - schema definition:
"""
contribution_table = schema.Table('contribution', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('contribution_seq_id', optional=True), primary_key=True),
    schema.Column('agentId', types.Integer,
        schema.ForeignKey('agent.id')),
    schema.Column('agentNetworkId', types.Integer,
        schema.ForeignKey('agent_network.id')),
    schema.Column('timeCreated', types.DateTime(), default=now),
    schema.Column('comment', types.Unicode(2000)),
    schema.Column('type', types.Unicode(340)),
    schema.Column('status', types.Unicode(100),default=u'Open'),
    schema.Column('currentValuation',  types.Float,default=0),
    schema.Column('valueIndic',  types.Integer,default=0),
    schema.Column('content',  types.Unicode(10000)),
)


"""
Contribution Contributors List - schema definition:
"""
contribution_contributor_table = schema.Table('contribution_contributor', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('contribution_contributor_seq_id', optional=True), primary_key=True),
    schema.Column('contributionId', types.Integer,
        schema.ForeignKey('contribution.id')),
    schema.Column('contributorId', types.Integer,
        schema.ForeignKey('agent.id')),
    schema.Column('percentage', types.FLOAT),   
)
   

"""
Contribution value- schema definition:
"""
contribution_value_table = schema.Table('contributionValue', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('contribution_value_seq_id', optional=True), primary_key=True),
    schema.Column('agentId', types.Integer,
        schema.ForeignKey('agent.id')),
    schema.Column('agentNetworkId', types.Integer,
        schema.ForeignKey('agent_network.id')),
    schema.Column('contributionId', types.Integer,
        schema.ForeignKey('contribution.id')),
    schema.Column('reputationGain',  types.Float,default=0),
    schema.Column('reputation',  types.Float,default=0),
)

"""
Evaluation - schema definition:
"""
evaluation_table = schema.Table('evaluation', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('evaluation_seq_id', optional=True), primary_key=True),
    schema.Column('agentId', types.Integer,
        schema.ForeignKey('agent.id')),   
    schema.Column('contributionId', types.Integer,
        schema.ForeignKey('contribution.id')),
    schema.Column('tokens', types.Float),
    schema.Column('stake', types.Float),
    schema.Column('reputation',  types.Float),
    schema.Column('contributionValueAfterEvaluation',  types.Float),
    schema.Column('timeCreated', types.DateTime(), default=now),
    schema.Column('comment', types.Unicode(2000)),

)



"""
Tag - schema definition:
"""
tag_table = schema.Table('tag', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('tag_seq_id', optional=True), primary_key=True),
    schema.Column('name', types.Unicode(255),nullable=False),
    schema.Column('contributionId', types.Integer,
        schema.ForeignKey('contribution.id'),nullable=False),
)

"""
Link - schema definition:
"""
link_table = schema.Table('link', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('link_seq_id', optional=True), primary_key=True),
    schema.Column('name', types.Unicode(255),nullable=False),
    schema.Column('contributionId', types.Integer,
        schema.ForeignKey('contribution.id'),nullable=False),
)

"""
Tag LINK - schema definition:
"""
tag_link_table = schema.Table('tag_link', metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('tag_link_seq_id', optional=True), primary_key=True),
    schema.Column('tagId', types.Integer,
        schema.ForeignKey('tag.id'),nullable=False),
    schema.Column('linkId', types.Integer,
        schema.ForeignKey('link.id'),nullable=False), 
                                                           
)


"""
Relationships - definitions
"""

orm.mapper(cls.Agent, agent_table, properties={
    'agentHandles':orm.relation(cls.AgentHandle, backref='agent'),
    'agentGroups':orm.relation(cls.AgentGroup, backref='agent'),
    'agentNetworks':orm.relation(cls.AgentNetwork, backref='agent'),
    'agentContributions':orm.relation(cls.Contribution, backref='agent'),
    'agentEvaluations':orm.relation(cls.Evaluation, backref='agent'),
})

orm.mapper(cls.AgentHandle, agent_handle_table)

orm.mapper(cls.AgentGroup, agent_group_table)

orm.mapper(cls.Group, group_table, properties={
    'agentGroups':orm.relation(cls.AgentGroup, backref='group'),  
    'agent':orm.relation(cls.Agent, backref='group'),
    'networks':orm.relation(cls.Network, backref='group'),                                                
})


orm.mapper(cls.Network, network_table, properties={
    'agentNetworks':orm.relation(cls.AgentNetwork, backref='network'),  
    'handles':orm.relation(cls.NetworkHandle, backref='network'),
    'agent':orm.relation(cls.Agent, backref='network'),                                                
})

orm.mapper(cls.AgentNetwork, agent_network_table, properties={
        'contributions':orm.relation(cls.Contribution),                                                              
})

orm.mapper(cls.NetworkHandle, network_handle_table)

orm.mapper(cls.Tag, tag_table, properties={
        'contribution':orm.relation(cls.Contribution, backref='tag'),                                                 
    
})


orm.mapper(cls.LINK, link_table, properties={
        'contribution':orm.relation(cls.Contribution, backref='link'),                                                 
    
})

orm.mapper(cls.TagLINK, tag_link_table, properties={
    'tag':orm.relation(cls.Tag, backref='links'),  
    'link':orm.relation(cls.LINK, backref='tags'),  
    
})

orm.mapper(cls.Contribution, contribution_table, properties={
    'evaluations':orm.relation(cls.Evaluation, backref='contribution'),  
    'contributors':orm.relation(cls.ContributionContributor, backref='contribution'),                                                  
    'agentNetwork':orm.relation(cls.AgentNetwork),
    'contributionValues':orm.relation(cls.ContributionValue),
    
})

orm.mapper(cls.ContributionContributor, contribution_contributor_table, properties={
    'agent':orm.relation(cls.Agent, backref='contributor'),                                                
})

orm.mapper(cls.ContributionValue, contribution_value_table)

orm.mapper(cls.Evaluation, evaluation_table)






