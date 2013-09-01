
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def NoActiveHostInCluster(vim, *args, **kwargs):
    '''A NoActiveHostInCluster fault is thrown when there is no host in a valid state
    in the given compute resource to perform a specified operation. This can
    happen, for example, if all the hosts are disconnected or in maintenance mode.'''

    obj = vim.client.factory.create('{urn:vim25}NoActiveHostInCluster')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'computeResource', 'dynamicProperty', 'dynamicType', 'faultCause',
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
