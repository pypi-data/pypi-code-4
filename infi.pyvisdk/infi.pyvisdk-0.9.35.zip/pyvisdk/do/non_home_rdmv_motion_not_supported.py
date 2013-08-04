
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def NonHomeRDMVMotionNotSupported(vim, *args, **kwargs):
    '''An operation on a powered-on virtual machine requests that an existing Raw Disk
    Mapping end up in a location other than the new home datastore for the virtual
    machine, but the host does not have that capability.'''

    obj = vim.client.factory.create('{urn:vim25}NonHomeRDMVMotionNotSupported')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 8:
        raise IndexError('Expected at least 9 arguments got: %d' % len(args))

    required = [ 'device', 'atSourceHost', 'failedHost', 'failedHostName', 'dynamicProperty',
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
