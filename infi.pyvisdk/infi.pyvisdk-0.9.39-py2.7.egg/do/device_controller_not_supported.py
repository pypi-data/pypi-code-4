
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def DeviceControllerNotSupported(vim, *args, **kwargs):
    '''The device in question is supported, but the device-controller combination is
    not supported.If this fault is returned as a subfault of
    DisallowedMigrationDeviceAttached, this indicates that although this device-
    controller combination may be supported on the destination host, the hosts do
    not support the requested migration of the virtual machine while using this
    device and controller.'''

    obj = vim.client.factory.create('{urn:vim25}DeviceControllerNotSupported')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'controller', 'device', 'reason', 'dynamicProperty', 'dynamicType',
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
