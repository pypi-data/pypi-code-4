
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def IORMNotSupportedHostOnDatastore(vim, *args, **kwargs):
    '''A IORMNotSupportedHostOnDatastore fault occurs when the datastore is connected
    to one or more hosts that do not support storage I/O resource management.'''

    obj = vim.client.factory.create('{urn:vim25}IORMNotSupportedHostOnDatastore')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'datastore', 'datastoreName', 'host', 'dynamicProperty', 'dynamicType',
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
