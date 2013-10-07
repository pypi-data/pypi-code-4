from __future__ import absolute_import

from minos.errors import ValidationError
from minos.validator import Validator


class DatetimeValidator(Validator):
    """Validate whether a field is a datetime object."""

    def _validate(self, instance, field, **kwargs):
        """Validate whether a field is a valid datetime object.

        :param object instance: Python object to be validated.
        :param string field: Name of field in *instance* to be validate.
        :param dict kwargs: Keyword arguments. See :ref:`keyword-args` for more info.
        :rtype: None
        :raises: :class:`~errors.ValidationError` if *field* is not a datetime.
        """
        value = getattr(instance, field)

        if not value:
            return

        try:
            from datetime import datetime
            assert isinstance(value, datetime)
        except Exception:
            msg = '%s %s' % (field, 'is an invalid date.')
            raise ValidationError(field, value, msg)
