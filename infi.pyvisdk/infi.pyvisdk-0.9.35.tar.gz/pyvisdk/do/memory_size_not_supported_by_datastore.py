
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def MemorySizeNotSupportedByDatastore(vim, *args, **kwargs):
    '''The memory amount of the virtual machine is not within the acceptable guest
    memory bounds supported by the virtual machine's datastore.'''

    obj = vim.client.factory.create('{urn:vim25}MemorySizeNotSupportedByDatastore')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'datastore', 'maxMemorySizeMB', 'memorySizeMB', 'dynamicProperty',
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
