from deployer.service import Service
from .base import Base


class ServiceTest(Base):

    def test_service(self):
        data = {
            'branch': 'lp:precise/mysql'}

        s = Service('db', data)
        self.assertEqual(s.name, "db")
        self.assertEqual(s.num_units, 1)
        self.assertEqual(s.constraints, None)
        self.assertEqual(s.config, None)

        data = {
            'branch': 'lp:precise/mysql',
            'constraints': "instance-type=m1.small",
            'options': {"services": "include-file://stack-include.yaml"},
            'num_units': 10}
        s = Service('db', data)
        self.assertEquals(s.num_units, 10)
        self.assertEquals(s.constraints, "instance-type=m1.small")
        self.assertEquals(
            s.config,
            {"services": "include-file://stack-include.yaml"})
