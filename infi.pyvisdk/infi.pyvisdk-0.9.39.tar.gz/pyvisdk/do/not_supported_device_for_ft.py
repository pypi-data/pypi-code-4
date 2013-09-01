
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def NotSupportedDeviceForFT(vim, *args, **kwargs):
    '''VMs with pvscsi or vmxnet3 virtual devices support Fault Tolerance only on 4.1
    or later hosts.'''

    obj = vim.client.factory.create('{urn:vim25}NotSupportedDeviceForFT')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 10:
        raise IndexError('Expected at least 11 arguments got: %d' % len(args))

    required = [ 'deviceLabel', 'deviceType', 'host', 'hostName', 'vm', 'vmName',
        'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
