"""empty message

Revision ID: 4e75cdb9aa63
Revises: 3a1c3456a8ad
Create Date: 2015-08-07 01:03:44.395000

"""

# revision identifiers, used by Alembic.
revision = '4e75cdb9aa63'
down_revision = '3a1c3456a8ad'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('user',sa.Column('slackId', sa.Unicode(255)))
    op.add_column('user',sa.Column('imgUrl72', sa.Unicode(255)))
    op.add_column('organization',sa.Column('channelName', sa.Unicode(255)))
    op.add_column('organization',sa.Column('channelId', sa.Unicode(255)))


def downgrade():
    pass

