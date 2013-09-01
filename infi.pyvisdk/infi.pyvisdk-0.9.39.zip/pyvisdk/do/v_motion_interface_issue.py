
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def VMotionInterfaceIssue(vim, *args, **kwargs):
    '''A VMotion interface has a problem. This may be an error or warning depending on
    the specific fault subclass. This is an error or warning only when migrating a
    powered-on virtual machine.'''

    obj = vim.client.factory.create('{urn:vim25}VMotionInterfaceIssue')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'atSourceHost', 'failedHost', 'failedHostEntity', 'dynamicProperty',
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
