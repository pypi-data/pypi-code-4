
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def SnapshotNoChange(vim, *args, **kwargs):
    '''This fault is for a snapshot request on a virtual machine whose state has not
    changed since a previous successful snapshot. For example, this occurs when you
    suspend the virtual machine, create a snapshot, and then request another
    snapshot of the suspended virtual machine.'''

    obj = vim.client.factory.create('{urn:vim25}SnapshotNoChange')

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
