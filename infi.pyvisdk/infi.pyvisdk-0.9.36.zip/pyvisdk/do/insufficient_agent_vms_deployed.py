
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def InsufficientAgentVmsDeployed(vim, *args, **kwargs):
    '''This fault is returned when the required number of deployed agent virtual
    machines is not currently deployed on a host and hence the host cannot be used
    to run client virtual machines.'''

    obj = vim.client.factory.create('{urn:vim25}InsufficientAgentVmsDeployed')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'currentNumAgentVms', 'hostName', 'requiredNumAgentVms', 'dynamicProperty',
        'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
