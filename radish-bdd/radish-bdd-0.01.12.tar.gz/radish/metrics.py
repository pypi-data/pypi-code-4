# -*- coding: utf-8 -*-


class Metrics(object):
    def __init__(self, features):
        self._features = features

    def calculate(self):
        metrics = {}
        for feature in self._features:
            for scenario in feature.get_scenarios():
                for step in scenario.get_steps():
                    if step.get_metric_indicators():
                        for indicator in step.get_metric_indicators():
                            try:
                                metrics[indicator] += 1
                            except KeyError:
                                metrics[indicator] = 1
        return metrics
