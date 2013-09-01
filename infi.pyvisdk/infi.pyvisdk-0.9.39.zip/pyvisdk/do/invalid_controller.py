
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def InvalidController(vim, *args, **kwargs):
    '''An InvalidController exception is thrown if a device refers to a controller
    that cannot be found. For example, an exception might be thrown if the client
    incorrectly passes a controller key, or if the client did not specify a
    controller where one is required (such as for disks or CD-ROMs).'''

    obj = vim.client.factory.create('{urn:vim25}InvalidController')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'controllerKey', 'deviceIndex', 'property', 'dynamicProperty', 'dynamicType',
        'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
