__version__ = '1.1'

import logging


log = logging.getLogger(__name__)


__all__ = [
    '__version__', 'TRUNCATE_LIMIT', 'USER_AGENT', 'Error', 'TelephoneNumberError', 'MessageError',
    'ActionError', 'LoginError', 'CreditError', 'GateError'
]


TRUNCATE_LIMIT = 459
USER_AGENT = 'python-smssluzba-cz'


class Error(Exception):
    """Base Error class for all package errors."""

    def __init__(self):
        super(Error, self).__init__(getattr(self, 'code'), getattr(self, 'message'))


class TelephoneNumberError(Error):

    code = '400;1'
    message = 'Telephone number is invalid.'


class MessageError(Error):

    code = '400;2'
    message = 'Message is empty.'


class ActionError(Error):

    code = '400'
    message = 'Unknown action.'


class LoginError(Error):

    code = '401'
    message = 'Invalid login credentials.'


class CreditError(Error):

    code = '402'
    message = 'Insufficient credit in your account.'


class GateError(Error):

    code = '503'
    message = 'SMS gate intercepted unknown error.'