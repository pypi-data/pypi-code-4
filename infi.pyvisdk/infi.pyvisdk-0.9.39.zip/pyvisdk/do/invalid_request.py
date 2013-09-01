
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def InvalidRequest(vim, *args, **kwargs):
    '''An InvalidRequest fault is thrown in response to a malformed request to the
    server that fails in the transport layer, e.g., the SOAP XML request was
    invalid. Subtypes of this fault, provides more specific transport errors, such
    as a using a reference to an unknown managed object type or method.'''

    obj = vim.client.factory.create('{urn:vim25}InvalidRequest')

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
