# -*- coding: utf-8 -*-
import unittest

import robotsuite
from plone.testing import layered

from collective.behavior.localskin.testing import (
    COLLECTIVE_BEHAVIOR_LOCALSKIN_ROBOT_TESTING
)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("test_localskin.robot"),
                layer=COLLECTIVE_BEHAVIOR_LOCALSKIN_ROBOT_TESTING),
    ])
    return suite
