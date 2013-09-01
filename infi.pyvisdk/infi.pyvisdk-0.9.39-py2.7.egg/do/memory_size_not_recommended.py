
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def MemorySizeNotRecommended(vim, *args, **kwargs):
    '''The memory amount of the virtual machine is not within the recommended memory
    bounds for the virtual machine's guest OS.'''

    obj = vim.client.factory.create('{urn:vim25}MemorySizeNotRecommended')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'maxMemorySizeMB', 'memorySizeMB', 'minMemorySizeMB', 'dynamicProperty',
        'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
