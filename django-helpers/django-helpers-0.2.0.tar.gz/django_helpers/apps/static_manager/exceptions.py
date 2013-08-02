__author__ = 'ajumell'


class StaticFileNotFoundException(Exception):
    def __init__(self, name):
        Exception.__init__(self, 'Static File "%s" not found.' % name)


class NotInProduction(Exception):
    def __init__(self):
        Exception.__init__(self, 'Static manager is not intended to use in production.')


class SyntaxErrorException(Exception):
    def __init__(self, obj):
        msg = 'Render JS Should only pass pure Javascript.'
        msg += '\nJavascript Syntax Error occured in object. %s' % str(type(obj))
        Exception.__init__(self, msg)


class PYESPRIMAException(Exception):
    def __init__(self):
        msg = "pyesprima is required for checking the syntax of javascript."
        msg += '\n Install it with pip install pyesprima.'

        Exception.__init__(self, msg)


class AppNameMissingException(Exception):
    def __init__(self):
        msg = "app_name is missing. It should be passed along with template tag."
        msg += " or the context should have a data with app_name."

        Exception.__init__(self, msg)