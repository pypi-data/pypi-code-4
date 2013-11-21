from deployer.service import Service
from .base import Base
from ..utils import parse_constraints


class ConstraintsTest(Base):

    def test_constraints(self):
        data = {
            'branch': 'lp:precise/mysql',
            'constraints': "instance-type=m1.small",
        }
        s = Service('db', data)
        self.assertEquals(s.constraints, "instance-type=m1.small")
        data = {
            'branch': 'lp:precise/mysql',
            'constraints': "cpu-cores=4 mem=2048M root-disk=10G",
        }
        s = Service('db', data)
        c = parse_constraints(s.constraints)
        self.assertEquals(s.constraints, "cpu-cores=4 mem=2048M root-disk=10G")
        self.assertEqual(c['cpu-cores'], 4)
        self.assertEqual(c['mem'], 2048)
        self.assertEqual(c['root-disk'], 10 * 1024)
