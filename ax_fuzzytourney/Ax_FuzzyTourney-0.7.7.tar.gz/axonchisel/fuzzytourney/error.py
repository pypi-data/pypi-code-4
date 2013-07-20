"""
Ax_FuzzyTourney Exceptions.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2013 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------


#
# Exception Hierarchy
#


class Error(Exception):
    """Base Exception class."""
    def __str__(self):
        return unicode(self).encode('utf-8')


class InputError(Error):
    """Exception raised when inputting data.

    Attributes:
        msg -- Error message
    """
    def __init__(self, msg):
        Error.__init__(self)
        self.msg = msg

    def __unicode__(self):
        return u"Ax_FuzzyTourney InputError: '{msg}'".format(msg=self.msg)


class ConfigError(Error):
    """Exception raised when loading/saving Ax_FuzzyTourney configs.

    Attributes:
        msg -- Error message
    """
    def __init__(self, msg):
        Error.__init__(self)
        self.msg = msg

    def __unicode__(self):
        return u"Ax_FuzzyTourney ConfigError: '{msg}'".format(msg=self.msg)


class ConfigSyntaxError(ConfigError):
    """Exception raised when loading Ax_FuzzyTourney configs with syntax errors.

    Attributes:
        msg -- Error message
    """
    def __init__(self, msg):
        ConfigError.__init__(self, msg)

    def __unicode__(self):
        return u"Ax_FuzzyTourney ConfigSyntaxError: '{msg}'".format(msg=self.msg)


class ConfigIncompleteError(ConfigError):
    """Exception raised when loading Ax_FuzzyTourney configs with incomplete data.

    Attributes:
        msg -- Error message
    """
    def __init__(self, msg):
        ConfigError.__init__(self, msg)

    def __unicode__(self):
        return u"Ax_FuzzyTourney ConfigIncompleteError: '{msg}'".format(msg=self.msg)


class ConfigValueError(ConfigError):
    """Exception raised when loading Ax_FuzzyTourney configs containing invalid values.

    Attributes:
        msg -- Error message
    """
    def __init__(self, msg):
        ConfigError.__init__(self, msg)

    def __unicode__(self):
        return u"Ax_FuzzyTourney ConfigValueError: '{msg}'".format(msg=self.msg)

