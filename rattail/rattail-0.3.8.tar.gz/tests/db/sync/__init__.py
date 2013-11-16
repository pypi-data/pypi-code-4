
from unittest import TestCase

from sqlalchemy import create_engine

from rattail.db import model


class SyncTestCase(TestCase):

    def setUp(self):
        self.local_engine = create_engine('sqlite://')
        self.remote_engines = {
            'one': create_engine('sqlite://'),
            'two': create_engine('sqlite://'),
            }
        model.Base.metadata.create_all(bind=self.local_engine)
        model.Base.metadata.create_all(bind=self.remote_engines['one'])
        model.Base.metadata.create_all(bind=self.remote_engines['two'])
