
import unittest
from mock import Mock

from pyramid import testing


class TestCase(unittest.TestCase):
    """
    Base class for all test suites.
    """

    def setUp(self):
        self.config = testing.setUp()
        # self.config = testing.setUp(settings={
        #         'mako.directories': [
        #             'rattail.pyramid:templates',
        #             'edbob.pyramid:templates',
        #             ],
        #         })

    def tearDown(self):
        testing.tearDown()


def mock_query():
    """
    Mock object used to simulate a ``sqlalchemy.Query`` instance.
    """

    query = Mock()
    query.return_value = query
    query.outerjoin.return_value = query
    query.join.return_value = query
    query.filter.return_value = query
    query.distinct.return_value = query
    query.order_by.return_value = query
    return query


# class DataTestCase(TestCase):
#     """
#     Base class for all test suites which require fixture data.
#     """

#     def setUp(self):
#         from sqlalchemy import create_engine
#         from edbob import db
#         from rattail.pyramid import Session
#         from edbob.db.util import install_core_schema
#         from edbob.db.extensions import activate_extension
#         from rattail.pyramid.tests.fixtures import load_fixtures

#         engine = create_engine('postgresql://rattail:1pKglVgdHOP1MYGVdUZr@localhost/rattail.test')

#         db.engines = {'default': engine}
#         db.engine = engine
#         db.Session.configure(bind=engine)
#         Session.configure(bind=engine)

#         install_core_schema(engine)
#         activate_extension('rattail', engine)
#         load_fixtures(engine)
#         super(DataTestCase, self).setUp()

#     # def tearDown(self):
#     #     from rattail.pyramid import Session
#     #     super(DataTestCase, self).tearDown()
#     #     Session.configure(bind=None)
