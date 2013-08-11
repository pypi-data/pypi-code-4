
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def InvalidOperationOnSecondaryVm(vim, *args, **kwargs):
    '''This fault is thrown when an attempt is made to invoke an operation on a
    secondary virtual machine that is only supported on the primary virtual machine
    of the fault tolerant group.'''

    obj = vim.client.factory.create('{urn:vim25}InvalidOperationOnSecondaryVm')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'instanceUuid', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
