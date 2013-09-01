
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def OperationDisallowedOnHost(vim, *args, **kwargs):
    '''An OperationDisallowedOnHost is thrown if an operation is diasllowed on host
    when a direct connection is used. Examples for such operations include VM
    powering on / memory hot-plug which could potentially violate hard-enforcement
    licenses if allowed on host. The functionality these operations provide is
    still available, but only through calls to an external entity.'''

    obj = vim.client.factory.create('{urn:vim25}OperationDisallowedOnHost')

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
