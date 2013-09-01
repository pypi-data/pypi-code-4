
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def VAppTaskInProgress(vim, *args, **kwargs):
    '''A specialized TaskInProgress when an operation is performed on a VM and it is
    failed due to a vApp-level operation is in progress. For example, while the
    power-on sequence is executed on a vApp, individual power-on's of child VMs are
    failed.'''

    obj = vim.client.factory.create('{urn:vim25}VAppTaskInProgress')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'task', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
