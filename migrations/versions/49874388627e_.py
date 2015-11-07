"""empty message

Revision ID: 49874388627e
Revises: 4113a638fb78
Create Date: 2015-11-05 01:14:29.334000

"""

# revision identifiers, used by Alembic.
revision = '49874388627e'
down_revision = '4113a638fb78'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('tag',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.Unicode(length=255)),
    sa.Column('contributionId', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['contributionId'], ['contribution.id'], ),
    sa.PrimaryKeyConstraint('id')
    )  
    
    op.create_table('link',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.Unicode(length=255)),
    sa.Column('contributionId', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['contributionId'], ['contribution.id'], ),
    sa.PrimaryKeyConstraint('id')
    )  
    
    op.create_table('tag_link',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('tagId', sa.INTEGER(), nullable=False),
    sa.Column('linkId', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['tagId'], ['tag.id'], ),
    sa.ForeignKeyConstraint(['linkId'], ['link.id'], ),
    sa.PrimaryKeyConstraint('id')
    )   
    pass


def downgrade():
    op.drop_table('tag_link')
    op.drop_table('link')
    op.drop_table('tag')
    pass
