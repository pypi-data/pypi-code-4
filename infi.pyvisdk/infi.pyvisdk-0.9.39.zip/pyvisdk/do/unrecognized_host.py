
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def UnrecognizedHost(vim, *args, **kwargs):
    '''A UnrecognizedHost is thrown if the VirtualCenter server fails to validate the
    identity of the host using host-key. If a reconnect is attempted on a host and
    if the host-key of the host has changed since the last successful connection
    attempt, (might be changed by another instance of VirtualCenter), VirtualCenter
    server will fail to recognize the host.'''

    obj = vim.client.factory.create('{urn:vim25}UnrecognizedHost')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'hostName', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
