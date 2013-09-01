
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def SoftRuleVioCorrectionDisallowed(vim, *args, **kwargs):
    '''The current DRS migration priority setting prevents generating a recommendation
    to correct the soft VM/Host affinity rules constraint violation for the VM so
    the violation will not be corrected.'''

    obj = vim.client.factory.create('{urn:vim25}SoftRuleVioCorrectionDisallowed')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'vmName', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
