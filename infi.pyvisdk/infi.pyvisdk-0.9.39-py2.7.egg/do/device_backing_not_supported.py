
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def DeviceBackingNotSupported(vim, *args, **kwargs):
    '''The device is backed by a backing type which is not supported for this
    particular device.If this fault is returned as a subfault of
    DisallowedMigrationDeviceAttached, this indicates that although this backing
    for the device may be supported on the destination host, the hosts do not
    support the requested migration of the virtual machine while using this device
    with this backing.'''

    obj = vim.client.factory.create('{urn:vim25}DeviceBackingNotSupported')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'backing', 'device', 'reason', 'dynamicProperty', 'dynamicType', 'faultCause',
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
