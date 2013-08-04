
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def DestinationSwitchFull(vim, *args, **kwargs):
    '''For one of the networks that the virtual machine is using, the corresponding
    switch on the host is full. If returned as part of migration checks, this is an
    error if either of the following is true, a warning otherwise:'''

    obj = vim.client.factory.create('{urn:vim25}DestinationSwitchFull')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 7:
        raise IndexError('Expected at least 8 arguments got: %d' % len(args))

    required = [ 'backing', 'connected', 'device', 'dynamicProperty', 'dynamicType',
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
