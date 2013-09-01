
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def SuspendedRelocateNotSupported(vim, *args, **kwargs):
    '''Either the source host product or the destination host product does not support
    relocation of suspended VMs. It must be supported on both, in order for the
    relocation to succeed. This fault is only applicable to suspended virtual
    machines.'''

    obj = vim.client.factory.create('{urn:vim25}SuspendedRelocateNotSupported')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 4:
        raise IndexError('Expected at least 5 arguments got: %d' % len(args))

    required = [ 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
