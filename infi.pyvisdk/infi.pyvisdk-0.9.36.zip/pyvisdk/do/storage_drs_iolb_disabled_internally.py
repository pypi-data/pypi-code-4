
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def StorageDrsIolbDisabledInternally(vim, *args, **kwargs):
    '''The fault occurs when Storage DRS disables IO Load balancing internally even
    though it is enabled by the user. This can happen due to one of the following
    reasons: 1. SIOC couldn't get enabled on at least one of the datastores 2. The
    connectivity between hosts and datastores is not uniform for all datastores. 3.
    Some statistics are not available to run IO load balancing'''

    obj = vim.client.factory.create('{urn:vim25}StorageDrsIolbDisabledInternally')

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
