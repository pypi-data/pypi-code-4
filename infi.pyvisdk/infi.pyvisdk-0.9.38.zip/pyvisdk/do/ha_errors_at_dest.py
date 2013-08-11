
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def HAErrorsAtDest(vim, *args, **kwargs):
    '''The destination compute resource is HA-enabled, and HA is not running properly.
    This will cause the following problems: 1) The VM will not have HA protection.
    2) If this is an intracluster VMotion, HA will not be properly informed that
    the migration completed. This can have serious consequences to the functioning
    of HA.'''

    obj = vim.client.factory.create('{urn:vim25}HAErrorsAtDest')

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
