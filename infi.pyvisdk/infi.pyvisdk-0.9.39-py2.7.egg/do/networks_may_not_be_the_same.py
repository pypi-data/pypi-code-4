
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def NetworksMayNotBeTheSame(vim, *args, **kwargs):
    '''Used as a warning if a virtual machine provisioning operation is done across
    datacenters. This warns that the network used by the virtual machine before and
    after the operation may not be the same even though the two networks have the
    same name. This is because network names are only unique within a datacenter.'''

    obj = vim.client.factory.create('{urn:vim25}NetworksMayNotBeTheSame')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'name', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
