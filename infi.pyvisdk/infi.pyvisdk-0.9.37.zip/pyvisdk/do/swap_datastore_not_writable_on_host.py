
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def SwapDatastoreNotWritableOnHost(vim, *args, **kwargs):
    '''The compute resource and/or virtual machine configurations indicate that when
    executing on the host the virtual machine should use a specific datastore, but
    host does not have read/write access to that datastore. (It may have no access
    at all, or read-only access.) If executing on the host the virtual machine
    would instead use its own directory for swapfile placement. This is a
    compatibility warning, not an error.'''

    obj = vim.client.factory.create('{urn:vim25}SwapDatastoreNotWritableOnHost')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'host', 'datastore', 'name', 'dynamicProperty', 'dynamicType', 'faultCause',
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
