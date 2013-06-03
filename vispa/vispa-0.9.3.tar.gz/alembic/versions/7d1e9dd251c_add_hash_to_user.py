"""Add hash to user

Revision ID: 7d1e9dd251c
Revises: 1e0a9d82ddc3
Create Date: 2012-09-25 17:44:10.314270

"""

# revision identifiers, used by Alembic.
revision = '7d1e9dd251c'
down_revision = '1e0a9d82ddc3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('user', sa.Column('hash', sa.UnicodeText()))

def downgrade():
    op.drop_column('user', 'hash')