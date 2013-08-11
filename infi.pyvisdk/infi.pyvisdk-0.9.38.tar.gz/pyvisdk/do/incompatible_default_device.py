
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def IncompatibleDefaultDevice(vim, *args, **kwargs):
    '''A default device (see defaultDevice for a definition) which the virtual machine
    is using is incompatible with the corresponding default device which will be
    created on the target host.This is an issue with powered-on or suspended
    migration under some circumstances. The problem is that in cases where the
    virtual machine must be recreated, it will have the default device created with
    default settings that are appropriate for the target host. If those are not
    compatible with the settings for that device that the virtual machine is
    currently using, then resuming the virtual machine on the target host might
    fail.This might happen if the device in question were reconfigured or the
    default is different between the source and the destination host. An example of
    a default device and associated setting which might cause this is
    videoRamSizeInKB. This is an error.'''

    obj = vim.client.factory.create('{urn:vim25}IncompatibleDefaultDevice')

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
