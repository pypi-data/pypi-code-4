VALIDATOR_FIELD = 'validator'

from functools import wraps
import re

# Inspired by / ported from validations in ActiveRecord 3
# http://rubyonrails.org

def validator(f):
    setattr(f, VALIDATOR_FIELD, True)
    return f


def _is_validator(obj):
    return hasattr(obj, VALIDATOR_FIELD) and \
            getattr(obj, VALIDATOR_FIELD) and \
            callable(obj)

class Validator(object):
    '''
    Subclass this class for validation that's not tied to a particular field.
    '''

    def __init__(self, **options):
        self.options = options

    def validate(self, instance):
        raise NotImplementedError


class FieldValidator(Validator):

    def __init__(self, fields, **options):
        self.fields = fields
        super(FieldValidator, self).__init__(**options)
        self.check_configuration()

    def validate(self, instance):
        for field in self.fields:
            value = getattr(instance, field, None)
            if (value == None and self.options.get('allow_none', None)) or \
               (not value and self.options.get('allow_false', None)):
                continue
            self.validate_field(instance, field, value)

    @property
    def message(self):
        return self.options.get('message', self.default_message)

    @property
    def default_message(self):
        raise NotImplementedError

    def validate_field(self, instance, field, value):
        raise NotImplementedError

    def check_configuration(self):
        pass

class ConditionValidator(FieldValidator):
    def validate_field(self, instance, field, value):
        if not self.condition_valid(instance, field, value):
            instance.errors.add(field, self.message)

class ClusionValidator(ConditionValidator):
    def check_configuration(self):
        if not (hasattr(self.choices, '__contains__') and \
                callable(self.choices.__contains__)):
            raise ValueError(
                "'choices' option is required and must provide an object " +
                "that implements the '__contains__' method"
            )

    @property
    def choices(self):
        return self.options.get('choices', None)

def validate_exclusion(instance, *fields, **options):
    ExclusionValidator(fields, **options).validate(instance)

class ExclusionValidator(ClusionValidator):
    @property
    def default_message(self):
        return "is a reserved value"
    def condition_valid(self, instance, field, value):
        return value not in self.choices

class InclusionValidator(ClusionValidator):
    @property
    def default_message(self):
        return "is not a valid choice"
    def condition_valid(self, instance, field, value):
        return value in self.choices

class PresenceValidator(ConditionValidator):
    @property
    def default_message(self):
        return "can't be blank"

    def condition_valid(self, instance, field, value):
        return bool(value)

class LengthValidator(FieldValidator):
    valid_tests = ['minimum', 'maximum', 'within', 'equals']

    def check_configuration(self):
        if not self.provided_tests:
            raise ValueError(
                "At least one of '%s' must be provided." \
                % "', '".join(self.valid_tests)
            )
        if 'within' in self.provided_tests:
            try:
                self.options['minimum'] = int(self.options['within'][0])
                self.options['maximum'] = int(self.options['within'][1])
            except (ValueError, TypeError, IndexError):
                raise ValueError(
                    "'within' must provide an iterable of the form (min, max)."
                )

    @property
    def provided_tests(self):
        return [v for v in self.valid_tests if v in self.options]

    @property
    def default_message(self):
        return None

    def validate_field(self, instance, field, value):
        try:
            value = len(value)
        except:
            value = len(str(value))

        for test in self.provided_tests:
            if test == 'minimum' and value <= self.options[test]:
                instance.errors.add(
                    field,
                    self.options.get(
                        'message', 
                        "is too short (must be at least %s characters)" % \
                        self.options[test]
                    )
                )
            elif test == 'maximum' and value >= self.options[test]:
                instance.errors.add(
                    field,
                    self.options.get(
                        'message',
                        "is too long (must be at most %s characters)" % \
                        self.options[test]
                    )
                )
            elif test == 'equals' and value != self.options[test]:
                instance.errors.add(
                    field,
                    self.options.get(
                        'message',
                        "must be exactly %s characters" % self.options[test]
                    )
                )

class FormatValidator(ConditionValidator):
    valid_tests = ['matches', 'without']
    
    def check_configuration(self):
        if not self.provided_tests:
            raise ValueError(
                "At least one of '%s' must be provided." \
                % "', '".join(self.valid_tests)
            )

    @property
    def provided_tests(self):
        return [v for v in self.valid_tests if v in self.options]

    @property
    def default_message(self):
        return "is invalid"

    def condition_valid(self, instance, field, value):
        return ('matches' not in self.provided_tests or \
                    bool(re.search(self.options['matches'], value))) and \
                ('without' not in self.provided_tests or \
                 not bool(re.search(self.options['without'], value)))


class AssociationValidator(ConditionValidator):
    @property
    def default_message(self):
        return "can't have errors"

    def condition_valid(self, instance, field, value):
        return value.valid()

def validate_exclusion(instance, *fields, **options):
    ExclusionValidator(fields, **options).validate(instance)
def validate_inclusion(instance, *fields, **options):
    InclusionValidator(fields, **options).validate(instance)
def validate_presence(instance, *fields, **options):
    PresenceValidator(fields, **options).validate(instance)
def validate_length(instance, *fields, **options):
    LengthValidator(fields, **options).validate(instance)
def validate_format(instance, *fields, **options):
    FormatValidator(fields, **options).validate(instance)
def validate_associated(instance, *fields, **options):
    AssociationValidator(fields, **options).validate(instance)


