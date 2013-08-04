
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def NotFound(vim, *args, **kwargs):
    '''A NotFound error occurs when a referenced component of a managed object cannot
    be found. The referenced component can be a data object type (such as a role or
    permission) or a primitive (such as a string).For example, if the missing
    referenced component is a data object, such as VirtualSwitch, the NotFound
    error is thrown. The NotFound error is also thrown if the data object is found,
    but the referenced name (for example, "vswitch0") is not.'''

    obj = vim.client.factory.create('{urn:vim25}NotFound')

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
