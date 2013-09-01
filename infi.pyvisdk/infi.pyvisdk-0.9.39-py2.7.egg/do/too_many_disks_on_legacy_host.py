
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def TooManyDisksOnLegacyHost(vim, *args, **kwargs):
    '''The VM has too many disks which can cause the VM to take a long time to power-
    on. This can result in migration taking a long time to complete or to fail due
    to timeout. This is a problem only for migration of powered-on virtual machines
    from or to ESX 2.x hosts.'''

    obj = vim.client.factory.create('{urn:vim25}TooManyDisksOnLegacyHost')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'diskCount', 'timeoutDanger', 'dynamicProperty', 'dynamicType', 'faultCause',
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
