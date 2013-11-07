#-*- coding: utf-8 -*-

from fresher.test.base import FresherTestCase

from unittest import TestCase


class PyunitTestCase(FresherTestCase, TestCase):
    """Support PyUnit tests."""

    def __init__(self, step_runner, step_registry, feature, scenario, feature_suite):
        FresherTestCase.__init__(self, step_runner, step_registry,
                                 feature, scenario, feature_suite)
        TestCase.__init__(self, scenario.name)

    def setUp(self):
        super(PyunitTestCase, self).setUp()
        for hook_impl in self.step_registry.get_hooks('before', self.scenario.get_tags()):
            hook_impl.run(self.scenario)

    def runScenario(self):
        for step in self.scenario.iter_steps():
            self.runStep(step, 3)
        self.last_step = None

    def tearDown(self):
        for hook_impl in reversed(self.step_registry.get_hooks('after', self.scenario.get_tags())):
            hook_impl.run(self.scenario)
