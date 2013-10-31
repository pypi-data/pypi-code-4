import sqlalchemy as sa
from sqlalchemy_utils.functions import in_
from tests import TestCase


class TestIn(TestCase):
    def create_models(self):
        class Building(self.Base):
            __tablename__ = 'building'
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255))

        self.Building = Building

    def test_in_for_multiple_attributes(self):
        print in_((User.name, User.id), [(1, u'someone'), (2, u'other guy')]
