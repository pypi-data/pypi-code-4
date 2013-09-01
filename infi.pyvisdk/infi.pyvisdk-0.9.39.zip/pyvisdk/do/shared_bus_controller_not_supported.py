
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def SharedBusControllerNotSupported(vim, *args, **kwargs):
    '''The virtual machine has one or more SCSI controllers that are engaged in bus
    sharing. This is an error when migrating a powered-on virtual machine, and can
    be returned as a subfault of DisallowedMigrationDeviceAttached.'''

    obj = vim.client.factory.create('{urn:vim25}SharedBusControllerNotSupported')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'device', 'reason', 'dynamicProperty', 'dynamicType', 'faultCause',
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
