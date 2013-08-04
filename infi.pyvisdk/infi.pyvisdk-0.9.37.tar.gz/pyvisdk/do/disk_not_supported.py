
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def DiskNotSupported(vim, *args, **kwargs):
    '''The host does not support the backings for the disks specified by the virtual
    machine. For example, this fault is thrown if a virtual machine is created from
    a template that specifies backings that the host does not have. Similarly, this
    fault is thrown if a virtual machine is registered on a host that does not
    support the specified backings.'''

    obj = vim.client.factory.create('{urn:vim25}DiskNotSupported')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'disk', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
