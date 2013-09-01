
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def IscsiFaultVnicHasMultipleUplinks(vim, *args, **kwargs):
    '''This fault indicates that the Virtual NIC has multiple uplinks and not suitable
    for iSCSI multi-pathing and can not be bound to iSCSI HBA.'''

    obj = vim.client.factory.create('{urn:vim25}IscsiFaultVnicHasMultipleUplinks')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'vnicDevice', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
