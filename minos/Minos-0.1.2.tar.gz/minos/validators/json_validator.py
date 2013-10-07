from __future__ import absolute_import
import json

from minos.errors import ValidationError
from minos.validator import Validator


class JSONValidator(Validator):
    """Validate whether a field is valid JSON."""

    def _validate(self, instance, field, **kwargs):
        """Validate whether a field's value is valid JSON. Expects a string of (potential) JSON, and attempts to parse it.

        :param object instance: Python object to be validated.
        :param string field: Name of field in *instance* to be validate.
        :param dict kwargs: Keyword arguments. See :ref:`keyword-args` for more info.
            In addition, can pass in a *json_validator* parameter, which overrides the default
            JSON parser (default is python's *json* module.)
        :rtype: None
        :raises: :class:`~errors.ValidationError` if *field* is not an email address.
        """

        value = getattr(instance, field)
        self.__validate(field, value, **kwargs)

    def __validate(self, key, value, **kwargs):

        # This is not a presence validator
        if not value or isinstance(value, dict) or isinstance(value, list):
            return

        if 'json_validator' in kwargs:
            json_parser = kwargs['json_validator']
        else:
            json_parser = json
        try:
            json_parser.loads(value)
        except ValueError:
            msg = '%s %s' % (key, 'is not valid JSON.')
            raise ValidationError(key, value, msg)
