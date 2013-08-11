
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def ReadOnlyDisksWithLegacyDestination(vim, *args, **kwargs):
    '''The virtual machine uses read-only (undoable or nonpersistent) disks that can
    cause a slower power on at the migration destination. As a result, VMtion could
    slow down considerably or timeout. This is an issue only for migration of
    powered-on virtual machines from an ESX host with version greater than 2.0.x to
    an ESX host with version 2.0.x. It will be an error if the number of such disks
    is great enough to cause timeout ( >= 3 ), or a warning otherwise.'''

    obj = vim.client.factory.create('{urn:vim25}ReadOnlyDisksWithLegacyDestination')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'roDiskCount', 'timeoutDanger', 'dynamicProperty', 'dynamicType', 'faultCause',
        'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
