"""empty message

Revision ID: 106654c69d00
Revises: 14e7b605f825
Create Date: 2015-09-26 01:47:08.124000

"""

# revision identifiers, used by Alembic.
revision = '106654c69d00'
down_revision = '14e7b605f825'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('milestone',sa.Column('contribution_id', sa.INTEGER()))
    
    op.create_table('contributionValue',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('contribution_id', sa.INTEGER(), nullable=True),
    sa.Column('users_organizations_id', sa.INTEGER(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('reputationGain', sa.FLOAT(), nullable=True),
    sa.Column('reputation', sa.FLOAT(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['contribution_id'], ['contribution.id'], ),
    sa.ForeignKeyConstraint(['users_organizations_id'], ['users_organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    pass


def downgrade():
    pass
