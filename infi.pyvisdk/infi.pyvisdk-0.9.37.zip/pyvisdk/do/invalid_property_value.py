
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def InvalidPropertyValue(vim, *args, **kwargs):
    '''The value of the property is not valid given the type of the property.'''

    obj = vim.client.factory.create('{urn:vim25}InvalidPropertyValue')

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
