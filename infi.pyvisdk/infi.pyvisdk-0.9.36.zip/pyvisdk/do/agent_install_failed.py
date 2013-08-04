
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def AgentInstallFailed(vim, *args, **kwargs):
    '''An AgentInstallFailed fault is thrown when VirtualCenter fails to install the
    VirtualCenter agent on a host. For example, a fault is thrown if the agent
    software cannot be uploaded to the host or an error occurred during the agent
    installation.'''

    obj = vim.client.factory.create('{urn:vim25}AgentInstallFailed')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'installerOutput', 'reason', 'statusCode', 'dynamicProperty', 'dynamicType',
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
