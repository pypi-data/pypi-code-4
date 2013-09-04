"""block

Revision ID: 2b9a31317d8c
Revises: None
Create Date: 2013-09-04 08:17:13.305512

"""

# revision identifiers, used by Alembic.
revision = '2b9a31317d8c'
down_revision = None

# SQLAlchemy object-relational mapper
from sqlalchemy import *
from sa_bitcoin.fields.hash_ import Hash256

from alembic import op

def upgrade():
    op.create_table('block',
        Column('id', Integer,
            Sequence('__'.join(['block','id','seq'])),
            primary_key = True),
        Column('version', SmallInteger, nullable=False),
        Column('parent_hash', Hash256, nullable=False),
        Column('merkle_hash', Hash256, nullable=False),
        Column('time', UNIXDateTime, nullable=False),
        Column('bits', Integer,
            CheckConstraint('16842752 <= bits and bits <= 486604799'),
            nullable = False),
        Column('nonce', UnsignedInteger, nullable=False),
        Column('hash', Hash256, nullable=False))
    op.create_index('_'.join(['ix','block','id']), 'block',
        'id'),
    op.create_index('_'.join(['ix','block','hash']), 'block',
        'hash', postgresql_using='hash')

def downgrade():
    op.drop_index('_'.join(['ix','block','hash']), 'block')
    op.drop_index('_'.join(['ix','block','id']), 'block')
    op.drop_table('block')
