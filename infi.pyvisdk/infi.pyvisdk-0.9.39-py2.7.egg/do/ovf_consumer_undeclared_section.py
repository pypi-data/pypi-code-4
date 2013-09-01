
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def OvfConsumerUndeclaredSection(vim, *args, **kwargs):
    '''A fault type indicating that an OVF consumer appended an undeclared section to
    an OST.An undeclared section means a section with a qualified type that the OVF
    consumer was not registered as a handler of.'''

    obj = vim.client.factory.create('{urn:vim25}OvfConsumerUndeclaredSection')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'qualifiedSectionType', 'extensionKey', 'extensionName', 'dynamicProperty',
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
