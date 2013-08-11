
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def QuiesceDatastoreIOForHAFailed(vim, *args, **kwargs):
    '''A QuiesceDatastoreIOForHAFailed fault occurs when the HA agent on a host cannot
    quiesce file activity on a datastore to be unmouonted or removed.'''

    obj = vim.client.factory.create('{urn:vim25}QuiesceDatastoreIOForHAFailed')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 10:
        raise IndexError('Expected at least 11 arguments got: %d' % len(args))

    required = [ 'ds', 'dsName', 'host', 'hostName', 'name', 'type', 'dynamicProperty',
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
