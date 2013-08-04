
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def NotEnoughCpus(vim, *args, **kwargs):
    '''The host hardware does not have enough CPU cores to support the number of
    virtual CPUs in the virtual machine.If the host is using hyperthreading,
    NotEnoughLogicalCpus is employed instead of NotEnoughCpus.'''

    obj = vim.client.factory.create('{urn:vim25}NotEnoughCpus')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'numCpuDest', 'numCpuVm', 'dynamicProperty', 'dynamicType', 'faultCause',
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
