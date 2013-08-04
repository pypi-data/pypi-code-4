
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def InsufficientStandbyMemoryResource(vim, *args, **kwargs):
    '''This fault is thrown by Distributed Power Management algorithm. It indicates
    that there are insufficient memory resources on standby hosts (if any) to meet
    the requirements of a given operation.'''

    obj = vim.client.factory.create('{urn:vim25}InsufficientStandbyMemoryResource')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'available', 'requested', 'dynamicProperty', 'dynamicType', 'faultCause',
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
