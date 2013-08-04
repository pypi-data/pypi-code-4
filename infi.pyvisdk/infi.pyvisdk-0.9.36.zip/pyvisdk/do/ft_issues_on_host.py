
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def FtIssuesOnHost(vim, *args, **kwargs):
    '''The FtIssuesOnHost fault reports issues that prevent a particular host from
    being used as the register or power on host for a Fault Tolerance secondary
    virtual machine'''

    obj = vim.client.factory.create('{urn:vim25}FtIssuesOnHost')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'errors', 'host', 'hostName', 'dynamicProperty', 'dynamicType', 'faultCause',
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
