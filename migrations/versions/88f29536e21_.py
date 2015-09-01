"""empty message

Revision ID: 88f29536e21
Revises: 4e75cdb9aa63
Create Date: 2015-09-01 08:47:07.487000

"""

# revision identifiers, used by Alembic.
revision = '88f29536e21'
down_revision = '4e75cdb9aa63'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('organization',sa.Column('a', sa.INTEGER()))
    op.add_column('organization',sa.Column('b', sa.INTEGER()))


def downgrade():
    pass
