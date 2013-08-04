
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def SnapshotCopyNotSupported(vim, *args, **kwargs):
    '''An attempt is being made to move or copy a virtual machine's disk that has
    associated snapshots, and preserving the snapshots is not supported because of
    some aspect of the virtual machine configuration, virtual machine power state,
    or the requested disk placement. This is an error for move operations (where
    the source is deleted after the copy) and a warning for clones (where the
    source is preserved).'''

    obj = vim.client.factory.create('{urn:vim25}SnapshotCopyNotSupported')

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
