"""empty message

Revision ID: 574b7c248857
Revises: 106654c69d00
Create Date: 2015-10-29 18:03:09.387000

"""

# revision identifiers, used by Alembic.
revision = '574b7c248857'
down_revision = '106654c69d00'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('user',sa.Column('twitterHandle', sa.Unicode(255)))
    pass


def downgrade():
    pass
