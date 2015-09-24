"""empty message

Revision ID: 14e7b605f825
Revises: 3e8042503c57
Create Date: 2015-09-24 15:27:27.098000

"""

# revision identifiers, used by Alembic.
revision = '14e7b605f825'
down_revision = '3e8042503c57'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('contribution',sa.Column('currentValuation', sa.FLOAT()))
    op.add_column('contribution',sa.Column('valueIndic', sa.INTEGER()))
    pass


def downgrade():
    pass
