
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def HostAccessRestrictedToManagementServer(vim, *args, **kwargs):
    '''Fault thrown when an attempt is made to adjust resource settings directly on a
    host that is being managed by VC. VC is currently the source of truth for all
    resource pools on the host. Examples of methods affected by this are:'''

    obj = vim.client.factory.create('{urn:vim25}HostAccessRestrictedToManagementServer')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'managementServer', 'dynamicProperty', 'dynamicType', 'faultCause',
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
