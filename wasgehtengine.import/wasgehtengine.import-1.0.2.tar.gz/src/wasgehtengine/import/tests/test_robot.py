from  wasgehtengine.import.testing import WASGEHTENGINE_IMPORT_FUNCTIONAL_TESTING
from plone.testing import layered
import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("robot_test.txt"),
                layer=WASGEHTENGINE_IMPORT_FUNCTIONAL_TESTING)
    ])
    return suite