
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def ConcurrentAccess(vim, *args, **kwargs):
    '''A ConcurrentAccess fault is thrown when an operation fails because another
    operation has modified the datastructure.For non-transactional operations, such
    as a recursive delete of a subtree of the inventory, the operation might fail
    with ConcurrentAccess if another thread has added a new entity to the
    hierarchy.'''

    obj = vim.client.factory.create('{urn:vim25}ConcurrentAccess')

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
