
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def InUseFeatureManipulationDisallowed(vim, *args, **kwargs):
    '''A InUseFeatureManipulationDisallowed fault is thrown if an
    Vim.LicenseAssignmentManager.SetFeatureInUse or
    Vim.LicenseAssignmentManager.ResetFeatureInUse call can not complete because a
    feature is not available or the manipulation is not allowed.'''

    obj = vim.client.factory.create('{urn:vim25}InUseFeatureManipulationDisallowed')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 4:
        raise IndexError('Expected at least 5 arguments got: %d' % len(args))

    required = [ 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
