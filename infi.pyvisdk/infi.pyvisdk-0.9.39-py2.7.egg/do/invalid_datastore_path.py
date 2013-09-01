
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def InvalidDatastorePath(vim, *args, **kwargs):
    '''An InvalidDatastorePath exception is thrown if a datastore path violates the
    expected format. The expected format is "[dsName] path", e.g. "[storage1]
    folder/Vm1.vmdk". This exception is also thrown if a datastore corresponding to
    the given datastore path is not found.'''

    obj = vim.client.factory.create('{urn:vim25}InvalidDatastorePath')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'datastorePath', 'datastore', 'name', 'dynamicProperty', 'dynamicType',
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
