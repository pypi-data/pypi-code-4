from sqlalchemy import *
from sqlalchemy.orm import *
from migrate import *
from migrate.changeset import *

meta = MetaData(migrate_engine)
meta.session = sessionmaker(bind=migrate_engine,
                            autoflush=True, autocommit=True)()

products = Table('stroller_product', meta, autoload=True)

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    Column('stock', Integer, nullable=True).create(products)
    Column('shiptime', Integer, nullable=True).create(products)
    pass

def downgrade():
    # Operations to reverse the above upgrade go here.
    products.c.stock.drop()
    products.c.shiptime.drop()
    pass
