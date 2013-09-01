
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def ThirdPartyLicenseAssignmentFailed(vim, *args, **kwargs):
    '''A ThirdPartyLicenseAssignmentFailed fault is thrown when the license assignment
    to a 3rd party module fails. The 3rd-party modules are installed and ran on ESX
    hosts, so this fault provides both host and module IDs.'''

    obj = vim.client.factory.create('{urn:vim25}ThirdPartyLicenseAssignmentFailed')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'host', 'module', 'reason', 'dynamicProperty', 'dynamicType', 'faultCause',
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
