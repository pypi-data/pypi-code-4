#-*- coding: utf-8 -*-

from __future__ import print_function
from fresher.cuke import FresherHandler
from fresher.prettyprint import FresherPrettyPrint

class ConsoleHandler(FresherHandler):

    def before_feature(self, feature):
        print(FresherPrettyPrint.feature(feature))
        print()

    def before_scenario(self, scenario):
        print(FresherPrettyPrint.scenario(scenario))

    def after_scenario(self, scenario):
        print()

    def step_failed(self, step, e):
        print(FresherPrettyPrint.step_failed(step))

    def step_ambiguous(self, step, e):
        print(FresherPrettyPrint.step_ambiguous(step))

    def step_undefined(self, step, e):
        print(FresherPrettyPrint.step_undefined(step))

    def step_exception(self, step, e):
        print(FresherPrettyPrint.step_exception(step))

    def after_step(self, step):
        print(FresherPrettyPrint.step_passed(step))
