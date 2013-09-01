
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def IscsiFaultVnicIsLastPath(vim, *args, **kwargs):
    '''This fault indicates that the given Virtual NIC is associated with the only
    path to the storage. Any attempt to unbind this from iSCSI HBA would result in
    storage being inaccessible.'''

    obj = vim.client.factory.create('{urn:vim25}IscsiFaultVnicIsLastPath')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'vnicDevice', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
