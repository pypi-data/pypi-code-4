
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def RDMNotPreserved(vim, *args, **kwargs):
    '''The virtual machine is configured with a Raw Disk Mapping. The host only
    supports Raw Disk Mappings in a limited fashion. After the migration, the RDM
    will function correctly, but it will be indistinguishable from a virtual disk
    when viewing the virtual machine's properties. This change will persist even if
    the virtual machine is migrated back to a host with full RDM support.This is a
    warning only for migrations to ESX 2.1.x hosts.'''

    obj = vim.client.factory.create('{urn:vim25}RDMNotPreserved')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'device', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
