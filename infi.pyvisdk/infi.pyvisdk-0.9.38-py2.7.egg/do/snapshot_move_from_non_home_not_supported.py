
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def SnapshotMoveFromNonHomeNotSupported(vim, *args, **kwargs):
    '''An attempt is being made to move a virtual machine's disk that has associated
    snapshots, and preserving the snapshots is not supported by the host because
    the disk is currently located somewhere other than the virtual machine's home
    datastore.'''

    obj = vim.client.factory.create('{urn:vim25}SnapshotMoveFromNonHomeNotSupported')

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
