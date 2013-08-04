
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def SnapshotIncompatibleDeviceInVm(vim, *args, **kwargs):
    '''Thrown if a snapshot operation cannot be performed on account of an
    incompatible device. This fault can be thrown for instance if a virtual machine
    uses a raw disk or a shared bus controller.'''

    obj = vim.client.factory.create('{urn:vim25}SnapshotIncompatibleDeviceInVm')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'fault', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
