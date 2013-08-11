
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def InventoryHasStandardAloneHosts(vim, *args, **kwargs):
    '''A InventoryHasStandardAloneHosts fault is thrown if an assignment operation
    tries to downgrade a license that does have allow hosts licensed with
    StandardAlone license in the inventory.'''

    obj = vim.client.factory.create('{urn:vim25}InventoryHasStandardAloneHosts')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'hosts', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
