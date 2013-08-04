
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def FaultToleranceVmNotDasProtected(vim, *args, **kwargs):
    '''A FaultToleranceVmNotDasProtected fault occurs when an Fault Tolerance VM is
    not protected by HA and the operation for terminating the primary VM or
    secondary VM is invoked.'''

    obj = vim.client.factory.create('{urn:vim25}FaultToleranceVmNotDasProtected')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'vm', 'vmName', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
