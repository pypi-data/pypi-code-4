
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def EightHostLimitViolated(vim, *args, **kwargs):
    '''Only virtual machines on eight different hosts can have a single virtual disk
    backing opened for read at once.This fault occurs when moving or powering on
    this virtual machine would cause a violation of the above constraint. This only
    occurs when multiple virtual machines are sharing a single disk backing.Note
    that there is no limit on the number of virtual machines who share a disk
    backings, so long as they are running on eight or fewer hosts.'''

    obj = vim.client.factory.create('{urn:vim25}EightHostLimitViolated')

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
