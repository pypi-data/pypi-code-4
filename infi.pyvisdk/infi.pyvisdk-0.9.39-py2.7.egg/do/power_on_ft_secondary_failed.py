
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def PowerOnFtSecondaryFailed(vim, *args, **kwargs):
    '''The PowerOnFtSecondaryFailed fault is thrown when the system is unable to power
    on a Fault Tolerance secondary virtual machine. It includes a list of failures
    on different hosts.'''

    obj = vim.client.factory.create('{urn:vim25}PowerOnFtSecondaryFailed')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 9:
        raise IndexError('Expected at least 10 arguments got: %d' % len(args))

    required = [ 'hostErrors', 'hostSelectionBy', 'rootCause', 'vm', 'vmName',
        'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
