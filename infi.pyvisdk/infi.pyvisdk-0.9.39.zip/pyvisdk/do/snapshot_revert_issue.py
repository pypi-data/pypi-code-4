
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def SnapshotRevertIssue(vim, *args, **kwargs):
    '''If the virtual machine is migrated to the destination host, there may be a
    problem reverting to one of its snapshots. This is a warning. If the snapshot
    name is not set and the event array is empty, then it the snapshot might
    possibly revert correctly. If the name is set and the event array is not empty
    then there surely will be a problem reverting to the snapshot.'''

    obj = vim.client.factory.create('{urn:vim25}SnapshotRevertIssue')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'errors', 'event', 'snapshotName', 'dynamicProperty', 'dynamicType',
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
