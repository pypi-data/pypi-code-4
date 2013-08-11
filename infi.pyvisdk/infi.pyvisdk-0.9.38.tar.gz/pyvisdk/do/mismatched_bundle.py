
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def MismatchedBundle(vim, *args, **kwargs):
    '''A MismatchedBundle fault is thrown when the bundle supplied for
    RestoreFirmwareConfiguration does not match the specifications of the host'''

    obj = vim.client.factory.create('{urn:vim25}MismatchedBundle')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 8:
        raise IndexError('Expected at least 9 arguments got: %d' % len(args))

    required = [ 'bundleBuildNumber', 'bundleUuid', 'hostBuildNumber', 'hostUuid',
        'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
