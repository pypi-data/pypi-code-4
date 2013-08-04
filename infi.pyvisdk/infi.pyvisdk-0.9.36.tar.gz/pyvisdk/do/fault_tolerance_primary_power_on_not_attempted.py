
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def FaultTolerancePrimaryPowerOnNotAttempted(vim, *args, **kwargs):
    '''This fault is used to report that VirtualCenter did not attempt to power on a
    Fault Tolerance secondary virtual machine because it was unable to power on the
    corresponding Fault Tolerance primary virtual machine.'''

    obj = vim.client.factory.create('{urn:vim25}FaultTolerancePrimaryPowerOnNotAttempted')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'primaryVm', 'secondaryVm', 'dynamicProperty', 'dynamicType', 'faultCause',
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
