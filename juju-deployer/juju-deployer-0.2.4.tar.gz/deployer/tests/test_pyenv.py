
import StringIO

from deployer.env.py import PyEnvironment
from deployer.errors import UnitErrors
from deployer.utils import setup_logging, ErrorExit


from .base import Base


class FakePyEnvironment(PyEnvironment):

    def __init__(self, name, status):
        super(FakePyEnvironment, self).__init__(name)
        self._status = status

    def status(self):
        return self._status


class PyEnvironmentTest(Base):

    def setUp(self):
        self.output = setup_logging(
            debug=True, verbose=True, stream=StringIO.StringIO())

    def test_wait_for_units_error_no_exit(self):
        env = FakePyEnvironment(
            "foo",
            {"services":
             {"wordpress":
              {"units":
               {"wordpress/0":
                {"agent-state": "install-error",
                 "machine": 1},
                },
               },
              },
             })
        try:
            env.wait_for_units(timeout=240, no_exit=True)
        except UnitErrors, e:
            self.assertEqual(1, len(e.errors))
            unit = e.errors[0]
            self.assertEqual("wordpress/0", unit["name"])
            self.assertEqual("install-error", unit["agent-state"])
            self.assertEqual(1, unit["machine"])
        else:
            self.fail("Did not get expected exception")

    def test_wait_for_units_error_exit(self):
        env = FakePyEnvironment(
            "foo",
            {"services":
             {"wordpress":
              {"units":
               {"wordpress/0":
                {"agent-state": "install-error",
                 "machine": 1},
                },
               },
              },
             })
        try:
            env.wait_for_units(timeout=240, no_exit=False)
        except ErrorExit:
            self.assertIn('The following units had errors:',
                          self.output.getvalue())
            self.assertIn('unit: wordpress/0: machine: 1 '
                          'agent-state: install-error',
                          self.output.getvalue())
        else:
            self.fail("Did not get expected exception")

    def test_wait_for_units_sub_error_no_exit(self):
        env = FakePyEnvironment(
            "foo",
            {"services":
             {"wordpress":
              {"units":
               {"wordpress/0":
                {"agent-state": "started",
                 "machine": 1,
                 "subordinates":
                 {"nrpe/0":
                  {"agent-state": "install-error"},
                  }
                 },
                },
               },
              },
             })
        try:
            env.wait_for_units(timeout=240, no_exit=True)
        except UnitErrors, e:
            self.assertEqual(1, len(e.errors))
            unit = e.errors[0]
            self.assertEqual("nrpe/0", unit["name"])
            self.assertEqual("install-error", unit["agent-state"])
            self.assertEqual(1, unit["machine"])
        else:
            self.fail("Did not get expected exception")

    def test_wait_for_units_no_error_no_exit(self):
        env = FakePyEnvironment(
            "foo",
            {"services":
             {"wordpress":
              {"units":
               {"wordpress/0":
                {"agent-state": "started",
                 "machine": 1,
                 "subordinates":
                 {"nrpe/0":
                  {"agent-state": "started"},
                  }
                 },
                },
               },
              },
             })
        try:
            env.wait_for_units(timeout=240, no_exit=True)
        except UnitErrors, e:
            self.fail("Unexpected exception: %s" % e)

    def test_wait_for_units_relation_error_no_exit(self):
        env = FakePyEnvironment(
            "foo",
            {"services":
             {"wordpress":
              {"units":
               {"wordpress/0":
                {"agent-state": "started",
                 "machine": 1,
                 "relation-errors":
                 {"nrpe": ["nrpe/1"]},
                 },
                },
               },
              },
             })
        try:
            env.wait_for_units(timeout=240, no_exit=True)
        except UnitErrors, e:
            self.assertEqual(1, len(e.errors))
            unit = e.errors[0]
            self.assertEqual("wordpress/0", unit["name"])
            self.assertEqual("relation-error: nrpe", unit["agent-state"])
            self.assertEqual(1, unit["machine"])
        else:
            self.fail("Did not get expected exception")

    def test_wait_for_units_subordinate_no_unit_no_error_no_exit(self):
        env = FakePyEnvironment(
            "foo",
            {"services":
             {"nrpe":
              {"subordinate": "true",
               "units": {},
               },
              },
             })
        try:
            env.wait_for_units(timeout=240, no_exit=True)
        except UnitErrors, e:
            self.fail("Unexpected exception: %s" % e)
