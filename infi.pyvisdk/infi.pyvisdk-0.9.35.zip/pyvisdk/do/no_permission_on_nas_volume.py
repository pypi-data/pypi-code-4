
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def NoPermissionOnNasVolume(vim, *args, **kwargs):
    '''This fault is thrown when an operation to configure a NAS volume fails because
    of insufficient user permissions. For CIFS volumes, this implies that the user
    specified in the spec does not have access to the network resource.'''

    obj = vim.client.factory.create('{urn:vim25}NoPermissionOnNasVolume')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'userName', 'name', 'dynamicProperty', 'dynamicType', 'faultCause',
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
