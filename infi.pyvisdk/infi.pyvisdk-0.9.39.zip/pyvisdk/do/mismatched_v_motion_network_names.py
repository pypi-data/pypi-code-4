
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def MismatchedVMotionNetworkNames(vim, *args, **kwargs):
    '''The source and destination hosts do not use the same network name for their
    VMotion interfaces. This is a warning for migrating powered-on virtual
    machines.'''

    obj = vim.client.factory.create('{urn:vim25}MismatchedVMotionNetworkNames')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'destNetwork', 'sourceNetwork', 'dynamicProperty', 'dynamicType', 'faultCause',
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
