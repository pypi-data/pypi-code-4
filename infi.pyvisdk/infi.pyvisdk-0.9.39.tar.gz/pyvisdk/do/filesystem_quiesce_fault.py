
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def FilesystemQuiesceFault(vim, *args, **kwargs):
    '''This fault is thrown when creating a quiesced snapshot failed because the
    create snapshot operation exceeded the time limit for holding off I/O in the
    frozen VM.This indicates that when we attempted to thaw the VM after creating
    the snapshot, we got an error back indicating that the VM was not frozen
    anymore. In this case, we roll back the entire snapshot create operation and
    throw this exception.'''

    obj = vim.client.factory.create('{urn:vim25}FilesystemQuiesceFault')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 4:
        raise IndexError('Expected at least 5 arguments got: %d' % len(args))

    required = [ 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
