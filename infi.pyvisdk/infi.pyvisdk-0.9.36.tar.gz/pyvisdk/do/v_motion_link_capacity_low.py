
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def VMotionLinkCapacityLow(vim, *args, **kwargs):
    '''The VMotion interface does not have the recommended capacity to support
    VMotion. VMotion is supported on links that have a speed of at least 1000 Mbps
    and are full duplex. This is a warning for migrating powered-on virtual
    machines.'''

    obj = vim.client.factory.create('{urn:vim25}VMotionLinkCapacityLow')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 8:
        raise IndexError('Expected at least 9 arguments got: %d' % len(args))

    required = [ 'network', 'atSourceHost', 'failedHost', 'failedHostEntity', 'dynamicProperty',
        'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
