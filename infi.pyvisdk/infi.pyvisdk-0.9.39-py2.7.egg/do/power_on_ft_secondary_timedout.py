
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def PowerOnFtSecondaryTimedout(vim, *args, **kwargs):
    '''PowerOnFtSecondaryTimedout exception is thrown when Virtual Center fails the
    operation to power on a Fault Tolerance secondary virtual machine because it is
    taking longer than expected.'''

    obj = vim.client.factory.create('{urn:vim25}PowerOnFtSecondaryTimedout')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'timeout', 'vm', 'vmName', 'dynamicProperty', 'dynamicType', 'faultCause',
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
