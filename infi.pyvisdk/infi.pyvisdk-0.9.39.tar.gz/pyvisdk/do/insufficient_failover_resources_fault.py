
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def InsufficientFailoverResourcesFault(vim, *args, **kwargs):
    '''This is thrown if an operation would violate the configured failover level of a
    HA cluster.In a HA cluster, virtual machines provide high availability by
    moving among physical machines in the event of a failure. HA Admission Control
    ensures that the total resource requirements for the set of virtual machines in
    a HA cluster does not exceed the resources that would be available in the
    worst-case scenario failure. If HA Admission Control is not used, physical
    machines may have insufficient resources to provide the expected level of
    service.This fault indicates that the virtual machine operation you attempted
    would have created a situation where the remaining physical machines would not
    meet the needs of the virtual machines in the event of a failure.'''

    obj = vim.client.factory.create('{urn:vim25}InsufficientFailoverResourcesFault')

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
