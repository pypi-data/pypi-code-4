
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def IncompatibleHostForFtSecondary(vim, *args, **kwargs):
    '''The IncompatibleHostForFtSecondary fault is thrown when an invalid host has
    been specified when calling CreateSecondaryVM_Task or EnableSecondaryVM_Task.'''

    obj = vim.client.factory.create('{urn:vim25}IncompatibleHostForFtSecondary')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'error', 'host', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
