from __future__ import absolute_import

from minos.errors import ValidationError

from decimal import Decimal
from minos.validator import Validator


class NumericalityValidator(Validator):
    """Validate numeric qualities of an instance's field."""

    def _validate(self, instance, field, **kwargs):
        """Validate a field's numericality. At minimum, this validator will validate whether a field
        appears to be numeric. Optionally, one can specify keyword arguments requiring that the field
        be an integer, as well as conditional behavior (e.g. that the field be greater than a given value.)

        :param object instance: Python object to be validated.
        :param string field: Name of field in *instance* to be validated.
        :param dict kwargs: Keyword arguments. See :ref:`keyword-args` for more info.
            Optionally, the following keywords can be specified:

            - only\_integer (bool): the field is also required to be an integer.
            - greater\_than\_or\_equal\_to (int): the field is required to be greater than or equal to this value.
            - less\_than\_or\_equal\_to (int): the field is required to be less than or equal to this value.
            - less\_than (int): the field is required to be less than this value.
            - greater\_than (int): the field is required to be greater than this value.
            - equal\_to (int): the field is required to be equal to this value.

        :rtype: None
        :raises: :class:`~errors.ValidationError` if *field* is not a number, or does not meet the numeric conditions (if given).
        """

        value = getattr(instance, field)
        self.__validate(field, value, **kwargs)

    def __validate(self, key, value, **kwargs):
        # This is not a presence validator
        if not value and not isinstance(value, int):
            return

        try:
            value = Decimal(str(value))
            assert isinstance(value, Decimal)
        except Exception:
            msg = '%s %s' % (key, 'must be a number')
            raise ValidationError(key, value, msg)

        try:
            if kwargs['only_integer']:
                assert value == value.quantize(Decimal('1'))
        except AssertionError:
            msg = '%s %s' % (key, 'must be an int')
            raise ValidationError(key, value, msg)
        except KeyError:
            pass

        try:
            assert value >= kwargs['greater_than_or_equal_to']
        except AssertionError:
            msg = '%s %s %s' % (key, 'greater than or equal to', str(kwargs['greater_than_or_equal_to']))
            raise ValidationError(key, value, msg)
        except KeyError:
            pass

        try:
            assert value <= kwargs['less_than_or_equal_to']
        except AssertionError:
            msg = '%s %s %s' % (key, 'less than or equal to', str(kwargs['less_than_or_equal_to']))
            raise ValidationError(key, value, msg)
        except KeyError:
            pass

        try:
            assert value < kwargs['less_than']
        except AssertionError:
            msg = '%s %s %s' % (key, 'must be less than or equal to', str(kwargs['less_than']))
            raise ValidationError(key, value, msg)
        except KeyError:
            pass

        try:
            assert value > kwargs['greater_than']
        except AssertionError:
            msg = '%s %s %s' % (key, 'must be greater than or equal to', str(kwargs['greater_than']))
            raise ValidationError(key, value, msg)
        except KeyError:
            pass
