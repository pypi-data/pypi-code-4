# -*- coding: utf-8 -*-

from radish.colorful import colorful


class RadishError(Exception):
    pass


class FeatureFileNotValidError(RadishError):
    """Raised when a feature file could not be parsed"""
    def __init__(self, feature_file):
        self._feature_file = feature_file

    def __str__(self):
        return colorful.red("The feature file '%s' is not valid" % (self._feature_file))


class StepLoadingError(RadishError):
    """Raised when a step decorator regex is not valid to compile"""
    def __init__(self, regex):
        self._regex = regex

    def __str__(self):
        return colorful.red("The step decorator regex '%s' is not valid to compile" % (self._regex))


class StepDefinitionNotFoundError(RadishError):
    """Raised when a step definition could not be found"""
    def __init__(self, step_sentence, step_filename):
        self._step_sentence = step_sentence
        self._step_filename = step_filename

    def __str__(self):
        return colorful.red("The step definition for '%s' from file '%s' could not be found" % (self._step_sentence, self._step_filename))


class FeatureFileNotFoundError(RadishError):
    """Raised when a feature file could not be found"""
    def __init__(self, path):
        self._path = path

    def __str__(self):
        return colorful.red("The feature file '%s' could not be found" % (self._path))


class BasedirNotFoundError(RadishError):
    """Raised when the basedir could not be found"""
    def __init__(self, basedir):
        self._basedir = basedir

    def __str__(self):
        return colorful.red("The basedir '%s' could not be found" % (self._basedir))


class StepDefinitionFileNotFoundError(RadishError):
    """Raised when the step definition file could not be found"""
    def __init__(self, root, pattern):
        self._root = root
        self._pattern = pattern

    def __str__(self):
        return colorful.red("The step definition file '%s' could not be found in the directory '%s'" % (self._pattern, self._root))


class NoMetricUtilFoundError(RadishError):
    """Raised if metric should be shown but no utils hook was found"""
    def __str__(self):
        return colorful.red("Could not found util hook to show metric - implement: utils( \"show_metrics\" )")


class ValidationError(RadishError):
    """Raised when a validation error occured during run"""
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return colorful.bold_red(self._msg)
