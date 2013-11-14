class WebAlertsException(Exception):
    """
    Root class of all exceptions defined in webalerts.

    """


class ConfigurationError(WebAlertsException):
    """
    Raised when there is an error in configurations.

    """


class SiteException(WebAlertsException):
    """
    Raised when a website-related error occurs, e.g. it fails to login or
    there is a network problem.

    """


class LoginError(SiteException):
    """
    Raised when website authentication fails.

    """


class ParseError(SiteException):
    """
    Raised when it fails to parse the returned HTML.

    """


class NotificationException(WebAlertsException):
    """
    Raised when a notification-related error occurs, e.g. it fails to send
    emails.

    """
