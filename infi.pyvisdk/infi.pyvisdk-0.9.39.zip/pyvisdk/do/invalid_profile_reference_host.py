
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def InvalidProfileReferenceHost(vim, *args, **kwargs):
    '''A InvalidProfileReferenceHost fault is thrown when a valid host is not
    associated with a profile in the Virtual Center inventory. This could be
    because there is no host assciated with the profile or because the associated
    host is incompatible with the profile.'''

    obj = vim.client.factory.create('{urn:vim25}InvalidProfileReferenceHost')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'host', 'profile', 'reason', 'dynamicProperty', 'dynamicType', 'faultCause',
        'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
