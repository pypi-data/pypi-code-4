from __future__ import absolute_import

import types
from minos.errors import ValidationError


class Validator(object):
    """
    Base class for model validators.

    If used in a class definition, the relevant arguments are set at instantiation
    and used by the mixin each time the model is re-validated. Otherwise,
    arguments can be provided for a given Validator at validation time.
    """

    def __init__(self, *args, **kwargs):

        self.args = args
        self.kwargs = kwargs

    def validate(self, instance, *args, **kwargs):
        kwargs = kwargs or self.kwargs
        if "if_" in kwargs:
            # Get if method, takes either a function name or a lambda function
            if isinstance(kwargs['if_'], types.LambdaType):
                if_method = kwargs['if_']
                if_condition = if_method(instance)
            else:
                if_method = getattr(instance, kwargs['if_'])

                #Call the method
                if hasattr(if_method, '__call__'):
                    if_condition = if_method()
                else:
                    raise UserWarning("If condition '%s' for '%s' is not callable" % (kwargs['if_'], self.__class__.__name__))
                    return

            if not if_condition:
                return

        try:
            self._validate(instance, *args, **kwargs)
        except ValidationError as validation_error:
            if "error_" in kwargs:
                validation_error.error = kwargs["error_"]
            raise validation_error

    def validate_wrapper(self, instance):
        """
        A wrapper around *.validate()* that uses the arguments provided at instantiation.
        """
        return self.validate(instance, self.args[0], **(self.kwargs))
