
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def UnsupportedDatastore(vim, *args, **kwargs):
    '''The virtual machine is not supported on the target datastore. This fault is
    thrown by provisioning operations when an attempt is made to create a virtual
    machine on an unsupported datastore (for example, creating a non-legacy virtual
    machine on a legacy datastore).'''

    obj = vim.client.factory.create('{urn:vim25}UnsupportedDatastore')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'datastore', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
