
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def InvalidResourcePoolStructureFault(vim, *args, **kwargs):
    '''This fault is thrown when an operation will cause the structure of a resource
    pool hiearchy to exceed its limit. The limits are typically imposed by the
    total number of nodes, maximum fan-out, and total depth of the hierarchy.'''

    obj = vim.client.factory.create('{urn:vim25}InvalidResourcePoolStructureFault')

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
