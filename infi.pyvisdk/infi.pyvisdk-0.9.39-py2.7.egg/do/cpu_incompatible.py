
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def CpuIncompatible(vim, *args, **kwargs):
    '''The host is not compatible with the CPU feature requirements of the virtual
    machine, for a particular CPUID register. A subclass of this fault may be used
    to express the incompatibilities in a more easily understandable format.'''

    obj = vim.client.factory.create('{urn:vim25}CpuIncompatible')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 9:
        raise IndexError('Expected at least 10 arguments got: %d' % len(args))

    required = [ 'desiredBits', 'host', 'level', 'registerBits', 'registerName',
        'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
