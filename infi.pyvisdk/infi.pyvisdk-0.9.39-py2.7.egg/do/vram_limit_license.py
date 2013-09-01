
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def VramLimitLicense(vim, *args, **kwargs):
    '''A VramLimitLicense fault is thrown if executing an operation would result in
    exceeding maximum allowed vRAM amount. For example, this could happen when
    powering on a VM, hot-plugging memory into a running VMm, etc.'''

    obj = vim.client.factory.create('{urn:vim25}VramLimitLicense')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'limit', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
