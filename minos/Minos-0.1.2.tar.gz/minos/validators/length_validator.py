from __future__ import absolute_import

from minos.errors import ValidationError
from minos.validator import Validator


class LengthValidator(Validator):
    """Validate a field's length."""

    def _validate(self, instance, field, **kwargs):
        """Validate a field's length. A fields length is determined using python's len() function.

        :param object instance: Python object to be validated.
        :param string field: Name of field in *instance* to be validate.
        :param dict kwargs: Keyword arguments. See :ref:`keyword-args` for more info.
            One of the following keywords is required (integer values):

            - greater\_than\_or\_equal\_to
            - less\_than\_or\_equal\_to
            - less\_than
            - greater\_than
            - equal\_to

        :rtype: None
        :raises: :class:`~errors.ValidationError` if *field* does not required legnth condition.
        """
        value = getattr(instance, field)
        self.__validate(field, value, **kwargs)

    def __validate(self, key, value, **kwargs):
        # This is not a presence validator
        if not value and not isinstance(value, int):
            return

        value = unicode(value)

        try:
            assert len(value) >= kwargs['greater_than_or_equal_to']
        except AssertionError:
            msg = '%s %s %s' % (key, 'length_greater_than_equal_to', str(kwargs['greater_than_or_equal_to']))
            raise ValidationError(key, value, msg)
        except KeyError:
            pass

        try:
            assert len(value) <= kwargs['less_than_or_equal_to']
        except AssertionError:
            msg = '%s %s %s' % (key, 'length_less_than_equal_to', str(kwargs['less_than_or_equal_to']))
            raise ValidationError(key, value, msg)
        except KeyError:
            pass

        try:
            assert len(value) < kwargs['less_than']
        except AssertionError:
            msg = '%s %s %s' % (key, 'length_must_be_less_than', str(kwargs['less_than']))
            raise ValidationError(key, value, msg)
        except KeyError:
            pass

        try:
            assert len(value) > kwargs['greater_than']
        except AssertionError:
            msg = '%s %s %s' % (key, 'length_must_be_greater_than', str(kwargs['greater_than']))
            raise ValidationError(key, value, msg)
        except KeyError:
            pass

        try:
            assert len(value) == kwargs['equal_to']
        except AssertionError:
            msg = '%s %s %s' % (key, 'length_must_be_equal_to', str(kwargs['equal_to']))
            raise ValidationError(key, value, msg)
        except KeyError:
            pass
