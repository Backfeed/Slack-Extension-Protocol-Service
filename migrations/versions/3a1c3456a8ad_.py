"""empty message

Revision ID: 3a1c3456a8ad
Revises: 4113a638fb78
Create Date: 2015-08-04 08:08:19.388000

"""

# revision identifiers, used by Alembic.
revision = '3a1c3456a8ad'
down_revision = '4113a638fb78'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('bid',
    sa.Column('weight', sa.FLOAT())
)


def downgrade():
    pass
