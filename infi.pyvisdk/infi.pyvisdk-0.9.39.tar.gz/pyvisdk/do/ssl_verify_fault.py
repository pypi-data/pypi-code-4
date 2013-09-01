
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def SSLVerifyFault(vim, *args, **kwargs):
    '''SSLVerifyFault is thrown by the host connect method if the VC server could not
    verify the authenticity of the host's SSL certificate. Currently, we do not
    distinguish the various possible reasons why the certificate could not be
    verified because we don't provide a way for the user to overwrite these reasons
    other than turning off SSL certificate verification completely. The only
    exception is the case when the certificate was rejected because it was self-
    signed. This is the most likely case when the user may want to overwrite the
    behavior by specifying the certificate's thumbprint in the ConnectSpec the next
    time the user connects to the host.'''

    obj = vim.client.factory.create('{urn:vim25}SSLVerifyFault')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'selfSigned', 'thumbprint', 'dynamicProperty', 'dynamicType', 'faultCause',
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
