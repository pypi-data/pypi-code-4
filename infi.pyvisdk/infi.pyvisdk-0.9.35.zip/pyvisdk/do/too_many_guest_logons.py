
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def TooManyGuestLogons(vim, *args, **kwargs):
    '''A TooManyGuestLogons exception is thrown when there are too many concurrent
    login sessions active in the guest. ReleaseCredentialsInGuest can be called on
    ticketed sessions that are no longer needed. This will decrease the number of
    concurrent sessions active in the guest.'''

    obj = vim.client.factory.create('{urn:vim25}TooManyGuestLogons')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 4:
        raise IndexError('Expected at least 5 arguments got: %d' % len(args))

    required = [ 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
