from __future__ import absolute_import


class ValidationError(Exception):
    """
    Error raised by Validator object if validation fails.

    :param string field: Field that failed validation.
    :param  value: Invalid value.
    :param string error: Error message from the validator.

    """

    field = None
    value = None
    error = None

    def __init__(self, field, value, error):
        self.field = field.strip("_")
        self.value = value
        self.error = error


class FormValidationError(Exception):
    """
    Error raised by Minos mixin if object validation fails.
    Collects and aggregates individual ValidationErrors into
    a single exception with a dictionary of field/error combinations.

    :param dict errors: A dictionary of validation errors. Keys correspond to
        validated fields in an instance, values are the error messages.
    """
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return str(self.errors)

    def __repr__(self):
        return "<FormValidationError '%s'>" % self.errors
