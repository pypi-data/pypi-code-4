
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def MultipleCertificatesVerifyFault(vim, *args, **kwargs):
    '''MultipleCertificatesVerifyFault is thrown by the host connect method
    ReconnectHost_Task as well as the methods to add a host to VirtualCenter
    (AddStandaloneHost_Task and AddHost_Task) if VirtualCenter detects that the
    host has different SSL certificates for different management ports. This can
    occur, for example, if an ESX 2.x host has different SSL certificates for the
    authd service (port 902) and the Management UI port (port 443). VirtualCenter
    is not able to manage such hosts. To fix this issue, the user should modify the
    host to ensure there is only one certificate for all services. Alternatively,
    different certificates are allowed as long as each certificate is verifiable
    (trusted) by the VirtualCenter server.'''

    obj = vim.client.factory.create('{urn:vim25}MultipleCertificatesVerifyFault')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'thumbprintData', 'dynamicProperty', 'dynamicType', 'faultCause',
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
