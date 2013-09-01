
import logging
from pyvisdk.exceptions import InvalidArgumentError

########################################
# Automatically generated, do not edit.
########################################

log = logging.getLogger(__name__)

def MigrationFault(vim, *args, **kwargs):
    '''Base object type for issues that can occur when reassigning the execution host
    of a virtual machine using migrate or relocate. These issues are typically used
    as argument in the MigrationEvent. When a MigrationFault is used as a value in
    a MigrationEvent, the type of MigrationEvent determines if the issue is a
    warning or an error (for example, MigrationHostWarningEvent or
    MigrationHostErrorEvent). When thrown as an exception, the fault is an
    error.Issues are categorized as errors or warnings according to the following
    criteria:If the virtual machine is powered on:If the virtual machine is powered
    off or suspended:'''

    obj = vim.client.factory.create('{urn:vim25}MigrationFault')

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
