
import unittest

from sqlalchemy import create_engine
from edbob.db import Session, Base
from edbob.db.util import install_core_schema
from edbob.db.extensions import activate_extension


__all__ = ['DataTestCase']


# TODO: This is just awful...
engine = create_engine('sqlite://')
Session.configure(bind=engine)
install_core_schema(engine)
activate_extension('rattail', engine)


class DataTestCase(unittest.TestCase):

    def setUp(self):
        self.session = Session()
        for table in reversed(Base.metadata.sorted_tables):
            if not table.name.startswith('batch.'):
                self.session.execute(table.delete())
        self.session.commit()

    def tearDown(self):
        self.session.close()
