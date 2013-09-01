
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def PlatformConfigFault(vim, *args, **kwargs):
    '''A PlatformConfigFault is a catch-all fault indicating that some error has
    occurred regarding the configuration of the host. Data about the fault is
    available and will be presented as a platform specific string.This information
    carried by this fault cannot be localized. Most likely this information will
    already have been localized to the locale of the server that generated this
    fault. Where possible, a more specific fault will be thrown.'''

    obj = vim.client.factory.create('{urn:vim25}PlatformConfigFault')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'text', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
