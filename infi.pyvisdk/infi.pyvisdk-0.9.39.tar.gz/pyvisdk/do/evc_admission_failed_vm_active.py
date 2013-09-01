
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def EVCAdmissionFailedVmActive(vim, *args, **kwargs):
    '''An attempt to move or add a host into an Enhanced VMotion Compatibility cluster
    has failed for the following reason:Therefore the host may not be admitted into
    the cluster, since its virtual machines may be using CPU features suppressed in
    the cluster.Note that in rare cases, this may occur even if the host's
    maxEVCModeKey corresponds to the EVC mode of the cluster. This means that even
    though that EVC mode is the best match for the host's hardware, the host still
    has some features beyond those present in the baseline for that EVC mode.'''

    obj = vim.client.factory.create('{urn:vim25}EVCAdmissionFailedVmActive')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'productName', 'productVersion', 'dynamicProperty', 'dynamicType',
        'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
