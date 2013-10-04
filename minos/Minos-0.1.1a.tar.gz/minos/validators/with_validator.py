from __future__ import absolute_import

from minos.errors import ValidationError
from minos.validator import Validator
import types


class WithValidator(Validator):
    """Validate a field with a given function."""

    def _validate(self, instance, field, **kwargs):
        """
        Validates a field with a user-specified function. The given function
        can either be a method in the given instance, or a inline lambda function.
        The specified method or function should return True or False.

        While this validator is extremely powerful and flexible, it should
        be regarded as a measure of last resort; Minos' validators generally
        give better performance and integration.

        :param object instance: Python object to be validated.
        :param string field: The name of the field in *instance* to be validated.
        :param dict kwargs: Keyword arguments. See :ref:`keyword-args` for more info.
            Addtionally, the following keyword arguments are required:

            - *with\_*: Either a string corresponding to a method name in *instance*, or
                a lambda function that takes the instance as an input.
        :rtype: None
        :raises: :class:`~errors.ValidationError` if the with\_ function returns False
        :raises: UserWarning if with\_ is not specified.
        """
        try:
            if isinstance(kwargs['with_'], types.LambdaType):
                assert kwargs['with_'](instance)
            else:
                validation_method = getattr(instance, kwargs['with_'])
                assert validation_method()
        except KeyError:
            raise UserWarning("Must provide 'with_' keyword argument to WithValidator")
        except AssertionError:
            msg = '%s %s' % (field, 'validation failed.')
            raise ValidationError(field, None, msg)
