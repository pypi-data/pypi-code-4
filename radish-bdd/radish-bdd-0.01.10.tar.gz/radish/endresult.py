# -*- coding: utf-8 -*-


class EndResult(object):
    def __init__(self, features):
        self._features = features
        self._total_features = 0
        self._total_scenarios = 0
        self._total_steps = 0

        self._passed_features = 0
        self._failed_features = 0
        self._skipped_features = 0

        self._passed_scenarios = 0
        self._failed_scenarios = 0
        self._skipped_scenarios = 0

        self._passed_steps = 0
        self._failed_steps = 0
        self._skipped_steps = 0

        self._total_features = len(features)
        for f in features:
            feature_outcome = f.has_passed()
            if feature_outcome:
                self._passed_features += 1
            elif feature_outcome is False:
                self._failed_features += 1
            elif feature_outcome is None:
                self._skipped_features += 1

            self._total_scenarios += len(f.get_scenarios())

            for s in f.get_scenarios():
                scenario_outcome = s.has_passed()
                if scenario_outcome:
                    self._passed_scenarios += 1
                elif scenario_outcome is False:
                    self._failed_scenarios += 1
                elif scenario_outcome is None:
                    self._skipped_scenarios += 1

                self._total_steps += len(s.get_steps())

                for step in s.get_steps():
                    step_outcome = step.has_passed()
                    if step_outcome:
                        self._passed_steps += 1
                    elif step_outcome is False:
                        self._failed_steps += 1
                    elif step_outcome is None:
                        self._skipped_steps += 1

    def have_all_passed(self):
        return self._total_features == self._passed_features

    def get_total_features(self):
        return self._total_features

    def get_features(self):
        return self._features

    def get_passed_features(self):
        return self._passed_features

    def get_failed_features(self):
        return self._failed_features

    def get_skipped_features(self):
        return self._skipped_features

    def get_total_scenarios(self):
        return self._total_scenarios

    def get_passed_scenarios(self):
        return self._passed_scenarios

    def get_failed_scenarios(self):
        return self._failed_scenarios

    def get_skipped_scenarios(self):
        return self._skipped_scenarios

    def get_total_steps(self):
        return self._total_steps

    def get_passed_steps(self):
        return self._passed_steps

    def get_failed_steps(self):
        return self._failed_steps

    def get_skipped_steps(self):
        return self._skipped_steps
