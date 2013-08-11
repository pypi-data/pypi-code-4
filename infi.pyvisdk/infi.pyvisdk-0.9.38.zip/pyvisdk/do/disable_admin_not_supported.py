
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def DisableAdminNotSupported(vim, *args, **kwargs):
    '''Fault thrown when an attempt is made to move a disk with associated snapshots
    to a destination host. If such a move were to occur, snapshots associated with
    the disk would be irrevocably lost. This is always an error.'''

    obj = vim.client.factory.create('{urn:vim25}DisableAdminNotSupported')

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
