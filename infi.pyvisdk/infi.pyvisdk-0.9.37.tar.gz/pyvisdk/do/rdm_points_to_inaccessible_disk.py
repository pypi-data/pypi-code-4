
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def RDMPointsToInaccessibleDisk(vim, *args, **kwargs):
    '''One of the virtual machine's virtual disks is a Raw Disk Mapping that is itself
    accessible, but points to a LUN that is inaccessible.'''

    obj = vim.client.factory.create('{urn:vim25}RDMPointsToInaccessibleDisk')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 8:
        raise IndexError('Expected at least 9 arguments got: %d' % len(args))

    required = [ 'fault', 'backing', 'connected', 'device', 'dynamicProperty', 'dynamicType',
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
