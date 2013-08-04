
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def DisallowedOperationOnFailoverHost(vim, *args, **kwargs):
    '''Fault thrown when an attempt is made to perform a disallowed operation on a
    host that has been configured as a failover host in an cluster that has High
    Availability enabled. See ClusterFailoverHostAdmissionControlPolicy. Examples
    of such operations are destroying a host, moving a host out of a cluster, or
    powering on a virtual machine on a specific host.'''

    obj = vim.client.factory.create('{urn:vim25}DisallowedOperationOnFailoverHost')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'host', 'hostname', 'dynamicProperty', 'dynamicType', 'faultCause',
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
