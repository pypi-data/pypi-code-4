
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def WillLoseHAProtection(vim, *args, **kwargs):
    '''This fault is reported when the execution of a storage vmotion or relocate
    operation would impact vSphere HA's ability to restart a VM. For storage
    vmotion, this fault is reported when HA protection will be lost after the
    vmotion completes. Consequently, HA would not restart the VM if it subsequently
    failed. For relocate, relocate is not supported on VMs that failed before the
    operation is attempted and are in the process of being restarted at the time
    the operation is performed.'''

    obj = vim.client.factory.create('{urn:vim25}WillLoseHAProtection')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'resolution', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
