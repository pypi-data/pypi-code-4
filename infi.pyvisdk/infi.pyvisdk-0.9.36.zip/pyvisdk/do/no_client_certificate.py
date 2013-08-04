
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def NoClientCertificate(vim, *args, **kwargs):
    '''This exception is thrown when a client has connected without supplying a
    certificate but the associated call expects that the client has done so.'''

    obj = vim.client.factory.create('{urn:vim25}NoClientCertificate')

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
