
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def InvalidDeviceOperation(vim, *args, **kwargs):
    '''An InvalidDeviceOperation exception is thrown if virtual machine creation or
    configuration fails because an invalid operation is attempted on the given
    device.'''

    obj = vim.client.factory.create('{urn:vim25}InvalidDeviceOperation')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 8:
        raise IndexError('Expected at least 9 arguments got: %d' % len(args))

    required = [ 'badFileOp', 'badOp', 'deviceIndex', 'property', 'dynamicProperty',
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
