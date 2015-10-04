"""empty message

Revision ID: 58516ccf520b
Revises: 88f29536e21
Create Date: 2015-09-15 17:14:29.953000

"""

# revision identifiers, used by Alembic.
revision = '58516ccf520b'
down_revision = '88f29536e21'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('milestone',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('ownerId', sa.INTEGER(), nullable=True),
    sa.Column('users_organizations_id', sa.INTEGER(), nullable=True),
    sa.Column('start_date', sa.DATETIME(), nullable=True),
    sa.Column('end_date', sa.DATETIME(), nullable=True),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.Column('title', sa.TEXT(), nullable=True),
    sa.Column('tokens', sa.FLOAT(), nullable=True),
    sa.Column('totalValue', sa.FLOAT(), nullable=True),
    sa.Column('destination_org_id', sa.INTEGER(), nullable=True),
    sa.Column('contributions', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['ownerId'], ['user.id'], ),
    sa.ForeignKeyConstraint(['users_organizations_id'], ['users_organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('milestone_contributer',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('milestone_id', sa.INTEGER(), nullable=True),
    sa.Column('contributor_id', sa.INTEGER(), nullable=True),
    sa.Column('percentage', sa.FLOAT(), nullable=True),
    sa.ForeignKeyConstraint(['contributor_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['milestone_id'], ['milestone.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('milestone_contribution',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('milestone_id', sa.INTEGER(), nullable=True),
    sa.Column('contribution_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['contribution_id'], ['contribution.id'], ),
    sa.ForeignKeyConstraint(['milestone_id'], ['milestone.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    
    op.create_table('milestone_bid',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('owner', sa.INTEGER(), nullable=True),
    sa.Column('milestone_id', sa.INTEGER(), nullable=True),
    sa.Column('tokens', sa.FLOAT(), nullable=True),
    sa.Column('stake', sa.FLOAT(), nullable=True),
    sa.Column('reputation', sa.FLOAT(), nullable=True),
    sa.Column('current_rep_to_return', sa.FLOAT(), nullable=True),
    sa.Column('milestone_value_after_bid', sa.FLOAT(), nullable=True),
    sa.Column('time_created', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['milestone_id'], ['milestone.id'], ),
    sa.ForeignKeyConstraint(['owner'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    

def downgrade():
    pass
