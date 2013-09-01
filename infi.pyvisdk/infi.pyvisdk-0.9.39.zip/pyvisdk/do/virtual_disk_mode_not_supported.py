
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def VirtualDiskModeNotSupported(vim, *args, **kwargs):
    '''The disk mode of the specified virtual disk is not supported.Typically, this
    fault is returned as part of a parent fault like
    VmConfigIncompatibleForFaultTolerance, indicating that the virtual disk's mode
    needs to be changed before fault tolerance can be enabled on the associated
    virtual machine.'''

    obj = vim.client.factory.create('{urn:vim25}VirtualDiskModeNotSupported')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'mode', 'device', 'reason', 'dynamicProperty', 'dynamicType', 'faultCause',
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
