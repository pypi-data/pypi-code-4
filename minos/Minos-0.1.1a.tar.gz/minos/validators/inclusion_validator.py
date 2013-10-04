from __future__ import absolute_import

from minos.errors import ValidationError
from minos.validator import Validator


class InclusionValidator(Validator):
    """
    Validate whether a field's value is in a list of accepted values.

    """
    def _validate(self, instance, field, **kwargs):
        """Validate whether a field's value is in a list of accepted values.

        :param object instance: Python object to be validated.
        :param string field: Name of field in *instance* to be validate.
        :param dict kwargs: Keyword arguments. See :ref:`keyword-args` for more info.
            Additionally, the following kwargs are required:
            - **in\_:** A list of acceptable values for *field*.
        :rtype: None
        :raises: :class:`~errors.ValidationError` if *field* is not an email address.
        :raises: UserWarning if *in\_* is not supplied.
        """
        value = getattr(instance, field)

        if not value:
            return

        if not kwargs.get('in_'):
            raise UserWarning("Must provide 'in_' keyword argument for inclusion validator")
            pass

        try:
            valid_values = kwargs.get('in_')
            assert value in valid_values
        except AssertionError:
            msg = '%s %s' % (field, 'is not valid.')
            raise ValidationError(field, None, msg)
