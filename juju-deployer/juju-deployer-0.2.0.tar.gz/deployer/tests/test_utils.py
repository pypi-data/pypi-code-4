from .base import Base
from deployer.utils import dict_merge


class UtilTests(Base):

    def test_relation_list_merge(self):
        self.assertEqual(
            dict_merge(
                {'relations': [['m1', 'x1']]},
                {'relations': [['m2', 'x2']]}),
            {'relations': [['m1', 'x1'], ['m2', 'x2']]})

    def test_no_rels_in_target(self):
        self.assertEqual(
            dict_merge(
                {'a': 1},
                {'relations': [['m1', 'x1'], ['m2', 'x2']]}),
            {'a': 1, 'relations': [['m1', 'x1'], ['m2', 'x2']]})
