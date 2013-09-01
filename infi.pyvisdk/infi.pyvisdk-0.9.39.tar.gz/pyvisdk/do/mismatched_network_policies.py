
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def MismatchedNetworkPolicies(vim, *args, **kwargs):
    '''The virtual machine network uses different offload or security policies on the
    destination host than on the source host. This is an error if the virtual
    machine is currently connected to the network, and a warning otherwise.'''

    obj = vim.client.factory.create('{urn:vim25}MismatchedNetworkPolicies')

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
