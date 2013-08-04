
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def UnusedVirtualDiskBlocksNotScrubbed(vim, *args, **kwargs):
    '''The unused disk blocks of the specified virtual disk have not been scrubbed on
    the file system.Typically, this fault is returned as part of a parent fault
    like VmConfigIncompatibleForFaultTolerance, indicating that the unused blocks
    of the virtual disk must be zeroed-out on the file system before before fault
    tolerance can be enabled on the associated virtual machine.'''

    obj = vim.client.factory.create('{urn:vim25}UnusedVirtualDiskBlocksNotScrubbed')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'backing', 'device', 'reason', 'dynamicProperty', 'dynamicType', 'faultCause',
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
