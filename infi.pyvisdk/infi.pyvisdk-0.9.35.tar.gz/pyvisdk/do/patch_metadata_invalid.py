
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def PatchMetadataInvalid(vim, *args, **kwargs):
    '''This fault is thrown if a patch query or installation operation fails because
    of a problem with the metadata associated with the patch. Typically, a subclass
    of this exception is thrown, indicating a problem such as the metadata is not
    found or the metadata is corrupted.'''

    obj = vim.client.factory.create('{urn:vim25}PatchMetadataInvalid')

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
