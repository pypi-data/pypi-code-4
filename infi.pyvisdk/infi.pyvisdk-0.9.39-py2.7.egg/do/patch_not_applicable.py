
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def PatchNotApplicable(vim, *args, **kwargs):
    '''This fault is thrown if a patch install fails because the patch is not
    applicable to the host. Typically, a subclass of this exception is thrown,
    indicating a problem such as the patch is superseded, already installed, or has
    dependencies missing, and so on.'''

    obj = vim.client.factory.create('{urn:vim25}PatchNotApplicable')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 5:
        raise IndexError('Expected at least 6 arguments got: %d' % len(args))

    required = [ 'patchID', 'dynamicProperty', 'dynamicType', 'faultCause', 'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
