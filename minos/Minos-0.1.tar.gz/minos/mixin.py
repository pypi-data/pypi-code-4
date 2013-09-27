from __future__ import absolute_import
import types


class MinosMixin(object):
    """
    Mixin class for python objects.

    Gives a framework for object validation. Provides a .validate() method, which
    introspects the class to find its validators, validates the object, and raises
    a FormValidationError if any attributes are invalid.

    See :ref:`Quickstart` section for more information and examples.
    """
    def validate(self, validator_attribute='validators'):
        """
        Perform validation of this model's attributes. Object validators are
        stored as a list in a specified attribute (*validator_attribute*), which
        the object is validated against serially.

        If a validator has an "if\_" keyword (See :ref:`keyword-args` for more info),
        it is checked here, before the validator is called.

        :param string validator_attribute: Attribute in object that contains a list of
            Validator objects.
        :return: None
        :raises: FormValidationError if any validators fail.
        """

        from minos.errors import ValidationError, FormValidationError

        errors = []

        for validator in getattr(self, validator_attribute, []):
            try:
                validator.validate_wrapper(self)
            except ValidationError as exp:
                errors.append(exp)

        if errors:
            error_dict = {}
            for exception in errors:
                if isinstance(exception, ValidationError):
                    # For now, allow only the first validation error per attribute
                    try:
                        error_dict[exception.field]
                        continue
                    except KeyError:
                        # TODO: Flip the switch to list of validation errors
                        # instead of one per key
                        # error_dict.setdefault(exp.key, []).append(exp.error)
                        error_dict[exception.field] = exception.error
                elif isinstance(exception, FormValidationError):
                    for error_key in exception.errors:
                        errors.append(ValidationError(error_key, None, exception.errors[error_key]))

            raise FormValidationError(error_dict)

        return True
