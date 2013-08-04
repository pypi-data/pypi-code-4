
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def CpuIncompatible1ECX(vim, *args, **kwargs):
    '''Convenience subclass for calling out some named features among the
    incompatibilities found in CPUID level 1 register ecx.'''

    obj = vim.client.factory.create('{urn:vim25}CpuIncompatible1ECX')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 17:
        raise IndexError('Expected at least 18 arguments got: %d' % len(args))

    required = [ 'aes', 'other', 'otherOnly', 'pclmulqdq', 'sse3', 'sse41', 'sse42', 'ssse3',
        'desiredBits', 'host', 'level', 'registerBits', 'registerName',
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
