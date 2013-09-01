
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def UnconfiguredPropertyValue(vim, *args, **kwargs):
    '''The property value has not been configured by the user, so the application
    cannot be started. This is thrown if a property value is the empty string and
    the types does not allow it. For example, for an integer type or a string where
    the minimum length is 1, and so forth.'''

    obj = vim.client.factory.create('{urn:vim25}UnconfiguredPropertyValue')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 9:
        raise IndexError('Expected at least 10 arguments got: %d' % len(args))

    required = [ 'category', 'id', 'label', 'type', 'value', 'dynamicProperty', 'dynamicType',
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
