
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def SwapDatastoreUnset(vim, *args, **kwargs):
    '''The compute resource and/or virtual machine configurations indicate that when
    executing on the host the virtual machine should use a swap datastore, but the
    host does not have a swap datastore configured. If executing on the host the
    virtual machine would instead use its own directory for swapfile placement.
    This is a compatibility warning, not an error. Note it is actually the common
    case for a host to not have a configured swap datastore, and the problem may
    rest with the compute resource and/or virtual machine configuration; therefore
    this is not a HostConfigFault.'''

    obj = vim.client.factory.create('{urn:vim25}SwapDatastoreUnset')

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
