
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def CannotAccessVmDevice(vim, *args, **kwargs):
    '''One of the virtual machine's devices uses a backing that is not accessible on
    the host.Following is a discussion of this fault's use in migration
    validation.This is an error if the device is currently connected and a warning
    otherwise. Devices that can be disconnected can only be connected if the
    virtual machine is powered on.The usage of this fault is slightly different if
    the backing of a device is inherently host-local, and therefore not shared or
    globally named among hosts. (Examples of such backings: physical CD-ROM drive,
    physical serial port.) If a device with such a backing is currently connected,
    that will be a migration error. If the device is disconnected, there will be a
    warning if no backing with the same name exists on the destination host. If the
    device is disconnected and a backing with the same name exists on the
    destination host, this is neither a warning nor an error case, even though the
    destination host's backing is not the same instance as the source host's. It is
    assumed that use of the host-local backing is what is desired for the device.'''

    obj = vim.client.factory.create('{urn:vim25}CannotAccessVmDevice')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'backing', 'connected', 'device', 'dynamicProperty', 'dynamicType',
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
