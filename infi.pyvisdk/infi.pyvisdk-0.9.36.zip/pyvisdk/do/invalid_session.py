
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def InvalidSession(vim, *args, **kwargs):
    '''This exception is thrown if a specified session is invalid. This can occur if
    the VirtualCenter session referred to by the cookie has timed out or has been
    closed.'''

    obj = vim.client.factory.create('{urn:sms}InvalidSession')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'sessionCookie', 'object', 'privilegeId', 'dynamicProperty', 'dynamicType',
        'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
