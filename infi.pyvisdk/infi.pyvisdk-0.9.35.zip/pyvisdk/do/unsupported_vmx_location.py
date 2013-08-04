
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def UnsupportedVmxLocation(vim, *args, **kwargs):
    '''ESX 3 Server products requires the .vmx file to be stored on NAS or VMFS3
    storage. If attempting to power on a virtual machine with the .vmx file stored
    on the service console, this fault will be thrown.'''

    obj = vim.client.factory.create('{urn:vim25}UnsupportedVmxLocation')

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
