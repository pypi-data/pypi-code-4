from __future__ import absolute_import

from minos.errors import ValidationError
from minos.validators.presence_validator import PresenceValidator
from minos.validator import Validator


class MinimumPresenceValidator(Validator):
    """Validate whether an instance has some subset of a list of attributes."""

    def _validate(self, instance, fields, **kwargs):
        """
        Validate whether an instance contains at least one field in a supplied list.
        Optionally, one can specify a *num\_requred* keyword parameter, requiring the
        instance to have at least *num_required* fields in the given list.

        :param object instance: Python object to be validated.
        :param list fields: An iterable object of strings, corresponding to the list of possibly required fields.
        :param dict kwargs: Keyword arguments. See :ref:`keyword-args` for more info.
            Optionally, a *num\_required* keyword can be specified, specifying the minimum
            number of fields *instance* is required to contain.
        :rtype: None
        :raises: :class:`~errors.ValidationError` if *instance* does not contain at least one
            (or *num_required*, if specified) of the listed fields.
        """

        num_required = kwargs.get('num_required', 1)
        num_found = 0
        for field in fields:
            try:
                PresenceValidator(field, **kwargs).validate_wrapper(instance)
                num_found = num_found + 1
                if num_found >= num_required:
                    return
            except ValidationError:
                pass

        # If we made it this far, we couldn't find any of the specified fields
        if num_found == 1:
            msg = '%s %s %s' % ('at least one of', ','.join(fields), 'is required.')
        else:
            msg = '%s %s %s' % ('at least {} of'.format(num_found), ','.join(fields), 'are required.')

        raise ValidationError(fields[0], None, msg)
