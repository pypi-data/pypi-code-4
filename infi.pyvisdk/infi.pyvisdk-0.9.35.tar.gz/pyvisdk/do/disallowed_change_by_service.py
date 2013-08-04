
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def DisallowedChangeByService(vim, *args, **kwargs):
    '''Fault thrown if the disallowed operation is invoked by the client. The change
    is disallowed because it conflicts with target state maintained by a service.
    The corresponding method is usually not disabled because only a subset of
    changes carried out by the method is disallowed. For example, an online extend
    executed via virtual machine reconfigure method is not allowed if replication
    is enabled on a virtual machine.'''

    obj = vim.client.factory.create('{urn:vim25}DisallowedChangeByService')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'disallowedChange', 'serviceName', 'dynamicProperty', 'dynamicType',
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
