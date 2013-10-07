from __future__ import absolute_import
from minos.errors import ValidationError
from sqlalchemy.schema import Column
from sqlalchemy.schema import ColumnDefault
from minos.validator import Validator


class PresenceValidator(Validator):
    """Validates whether an object has a given field."""

    def _validate(self, instance, field, **kwargs):
        """
        Validate whether an instance has a given field, and that that field is non-empty.

        The field's value is required to return True to python's bool() function
        (i.e. empty strings or empty containers will cause a validation error)

        **SQLAlchemy Note:** If the field to be validated is a Column object in SQLAlchemy model
        with a default value specified, the default value will be checked if the field is otherwise
        empty.

        :param object instance: Python object to be validated.
        :param string fields: The name of the field that *instance* is required to contain.
        :param dict kwargs: Keyword arguments. See :ref:`keyword-args` for more info.
        :rtype: None
        :raises: :class:`~errors.ValidationError` if *instance* does not contain the listed field.
        """

        try:
            value = getattr(instance, field)
        except AttributeError:
            msg = '%s %s' % (field, 'is required.')
            raise ValidationError(field, None, msg)

        # If the SQLA column definition has a default value declarded, the presence validator should always pass
        if not value:
            if hasattr(instance.__class__, "__mapper__"):
                col = instance.__class__.__mapper__.columns.__dict__['_data'].get(field)
                if isinstance(col, Column) and isinstance(col.default, ColumnDefault):
                    return True
            else:
                msg = '%s %s' % (field, 'is required.')
                raise ValidationError(field, None, msg)

        self.__validate(field, value, **kwargs)

    def __validate(self, key, value, **kwargs):

        try:
            if value or value == False:
                assert True
            else:
                assert False
        except AssertionError:
            msg = '%s %s' % (key, 'is required.')
            raise ValidationError(key, value, msg)
