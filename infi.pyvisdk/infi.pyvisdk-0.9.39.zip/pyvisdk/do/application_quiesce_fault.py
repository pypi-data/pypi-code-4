
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def ApplicationQuiesceFault(vim, *args, **kwargs):
    '''This fault is thrown when creating a quiesced snapshot failed because the
    (user-supplied) custom pre-freeze script in the virtual machine exited with a
    non-zero return code.This indicates that the script failed to perform its
    quiescing task, which causes us to fail the quiesced snapshot operation.'''

    obj = vim.client.factory.create('{urn:vim25}ApplicationQuiesceFault')

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
