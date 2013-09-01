
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def InvalidDrsBehaviorForFtVm(vim, *args, **kwargs):
    '''This fault is thrown when an attempt is made to set the DRS behavior of an FT
    VM to an unsupported value. Currently, the only supported behavior is .'''

    obj = vim.client.factory.create('{urn:vim25}InvalidDrsBehaviorForFtVm')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'vm', 'vmName', 'invalidProperty', 'dynamicProperty', 'dynamicType',
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
