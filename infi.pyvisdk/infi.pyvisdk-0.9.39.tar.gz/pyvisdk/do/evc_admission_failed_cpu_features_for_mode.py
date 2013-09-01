
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def EVCAdmissionFailedCPUFeaturesForMode(vim, *args, **kwargs):
    '''The host's CPU hardware is a family/model that should support the Enhanced
    VMotion Compatibility mode of the cluster, but some necessary CPU features are
    not present.'''

    obj = vim.client.factory.create('{urn:vim25}EVCAdmissionFailedCPUFeaturesForMode')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'currentEVCModeKey', 'productName', 'productVersion', 'dynamicProperty',
        'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
