
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def PatchMetadataNotFound(vim, *args, **kwargs):
    '''This fault is thrown if the metadata associated with a patch is not found when
    a patch query or install is attempted.'''

    obj = vim.client.factory.create('{urn:vim25}PatchMetadataNotFound')

    # do some validation checking...
    if (len(args) + len(kwargs)) < 6:
        raise IndexError('Expected at least 7 arguments got: %d' % len(args))

    required = [ 'metaData', 'patchID', 'dynamicProperty', 'dynamicType', 'faultCause',
        'faultMessage' ]
    optional = [  ]

    for name, arg in zip(required+optional, args):
        setattr(obj, name, arg)

    for name, value in kwargs.items():
        if name in required + optional:
            setattr(obj, name, value)
        else:
            raise InvalidArgumentError("Invalid argument: %s.  Expected one of %s" % (name, ", ".join(required + optional)))

    return obj
