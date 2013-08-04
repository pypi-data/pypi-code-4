
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def GuestAuthenticationChallenge(vim, *args, **kwargs):
    '''Fault is thrown when a call to AcquireCredentialsInGuest requires a challenge
    response in order to authenticate in the guest. The authToken string in
    serverChallenge contains a base64 encoded challenge token.'''

    obj = vim.client.factory.create('{urn:vim25}GuestAuthenticationChallenge')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'serverChallenge', 'sessionID', 'dynamicProperty', 'dynamicType', 'faultCause',
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
