
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def RuleViolation(vim, *args, **kwargs):
    '''The virtual machine if powered on, would violate an affinity/anti-affinity
    rule. In this case, the VM can still be powered on manually by a user who knows
    what they are doing, but VirtualCenter will never automatically move or power
    on a VM such that it triggers the violation.'''

    obj = vim.client.factory.create('{urn:vim25}RuleViolation')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'host', 'rule', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
