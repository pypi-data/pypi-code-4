
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def IscsiFaultInvalidVnic(vim, *args, **kwargs):
    '''This fault indicates an attempt is made to bind a Virtual NIC to an iSCSI
    adapter where the Virtual NIC has no association with the adapter. For ex: The
    uplink for the given Virtual NIC is not valid for the iSCSI HBA.'''

    obj = vim.client.factory.create('{urn:vim25}IscsiFaultInvalidVnic')

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
