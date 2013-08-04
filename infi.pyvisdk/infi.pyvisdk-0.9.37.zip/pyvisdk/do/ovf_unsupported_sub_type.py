
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def OvfUnsupportedSubType(vim, *args, **kwargs):
    ''''''

    obj = vim.client.factory.create('{urn:vim25}OvfUnsupportedSubType')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 9:
        raise IndexError('Expected at least 10 arguments got: %d' % len(args))

    required = [ 'deviceSubType', 'deviceType', 'elementName', 'instanceId', 'lineNumber',
        'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
