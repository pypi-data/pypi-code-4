
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def AlreadyConnected(vim, *args, **kwargs):
    '''AlreadyConnect fault is thrown by the host connect method if the host is
    already connected to a VirtualCenter server. This might occur if the host has
    been added more than once in the same VirtualCenter in different folders or
    compute resources.'''

    obj = vim.client.factory.create('{urn:vim25}AlreadyConnected')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'name', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
