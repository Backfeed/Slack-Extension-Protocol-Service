"""empty message

Revision ID: 3e8042503c57
Revises: 58516ccf520b
Create Date: 2015-09-21 15:30:56.869000

"""

# revision identifiers, used by Alembic.
revision = '3e8042503c57'
down_revision = '58516ccf520b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('organization',sa.Column('reserveTokens', sa.FLOAT()))
    op.add_column('milestone_bid',sa.Column('weight', sa.FLOAT()))
    pass


def downgrade():
    pass
