
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def VmfsAmbiguousMount(vim, *args, **kwargs):
    '''An 'VmfsAmbiguousMount' fault occurs when ESX is unable to resolve the extents
    of a VMFS volume unambiguously. This is thrown only when a VMFS volume has
    multiple extents and multiple copies of VMFS volumes are available. VMFS layer
    will not be able to determine how to re-construct the VMFS volume as multiple
    choices are available.'''

    obj = vim.client.factory.create('{urn:vim25}VmfsAmbiguousMount')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'uuid', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
