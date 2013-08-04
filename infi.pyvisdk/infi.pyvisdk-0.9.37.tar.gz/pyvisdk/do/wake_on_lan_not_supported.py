
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def WakeOnLanNotSupported(vim, *args, **kwargs):
    '''The virtual machine and at least one of its virtual NICs are configured to use
    Wake-on-LAN, but the host does not support Wake-on-LAN for the virtual
    machine's selected guest OS.'''

    obj = vim.client.factory.create('{urn:vim25}WakeOnLanNotSupported')

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
