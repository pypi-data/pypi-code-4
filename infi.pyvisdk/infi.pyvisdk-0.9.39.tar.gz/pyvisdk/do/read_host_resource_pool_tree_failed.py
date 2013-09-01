
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def ReadHostResourcePoolTreeFailed(vim, *args, **kwargs):
    '''Fault thrown on host connect if we were unable to correctly read the existing
    tree on the root. This is bad because then we don't know the available
    resources on the host, and all kinds of admission control will fail. This just
    allows for more robust error handling - we should be able to read the existing
    hierarchy under normal conditions.'''

    obj = vim.client.factory.create('{urn:vim25}ReadHostResourcePoolTreeFailed')

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
