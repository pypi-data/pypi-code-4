# -*- coding: utf-8 -*-
"""
Models for different kind of input fields that manage validation, type, error, aso.

Heavily based on Django forms principles

TODO: * Option for each field (just to be implemented on the base class) to allow
        colorisation (that will apply on label and errors), that might be used
        in a global option for a form;
      * Split validator, field and form parts in an input module directory;
      * Creation of a simple base form, to globally manage the options
        of a group of fields;
"""
import sys
from string import Template

INPUT_REQUIRED_ERROR = u"This input is required"
INPUT_INVALID_ERROR = u"This is not a valid value"
INPUT_MINCHARS_ERROR = u'Ensure this value has at least ${min_length} characters (it has ${show_value})'
INPUT_MAXCHARS_ERROR = u'Ensure this value has at most ${max_length} characters (it has ${show_value})'
INPUT_MINLENGTH_ERROR = u'Ensure this value is greater than or equal to ${min_length}'
INPUT_MAXLENGTH_ERROR = u'Ensure this value is less than or equal to ${max_length}'

class ValidationError(Exception):
    """
    Signature of an exception raised by the validator
    """
    pass

class RequiredValue(Exception):
    """
    Signature of an exception raised when a required value is missing
    """
    pass

EMPTY_VALUES = (None, '', [], (), {})

def boolean_validator(value, **kwargs):
    """
    Validation of a boolean choice (yes/no)

    This only checks that the value is among possible choices (yes/no). If yes, True is
    always returned. Otherwise, a ValidationError is raised.
    
    :type value: string
    :param value: Value to validate.
    
    :type kwargs: any
    :param kwargs: Accepts all possible named arguments. Must contain at least
                   ``choices_false`` and``choices_true`` both lists of strings 
                   respectively of possible values to validate positively the selection,
                   and the values to invalidate the selection.
    :rtype: bool
    :return: Always returns True when validation is done. Otherwise, raises
             a `ValidationError` exception.
    """
    if value:
        value = value.strip()
        if len(value)>0:
            if value in kwargs['choices_true'] or value in kwargs['choices_false']:
                return True
    raise ValidationError, 'invalid'

def minlength_validator(value, **kwargs):
    """
    Validation for a minimum value


    Raises a`ValidationError` exception if the input is smaller than the minimum
    value.
    
    :type value: int
    :param value: Value to validate.
    
    :type kwargs: any
    :param kwargs: Accepts all possible named arguments. Must contain at least
                   ``min_length`` that contains an integer specifying the minmum value.
    """
    if kwargs.get('min_length', False) and value<kwargs['min_length']:
        raise ValidationError, 'min_length'

def maxlength_validator(value, **kwargs):
    """
    Validation for a maximal value
    
    Raises a `ValidationError` exception if the input is greater than the maximum value.
    
    :type value: int
    :param value: Value to validate.
    
    :type kwargs: any
    :param kwargs: Accepts all possible named arguments. Must contain at least
                   ``max_length`` that contains an integer specifying the maximum value.
    """
    if kwargs.get('max_length', False) and value>kwargs['max_length']:
        raise ValidationError, 'max_length'

def string_validator(value, **kwargs):
    """
    Validation characters string
    
    Checks if the input is of type ``string``. If not, raises a`ValidationError`
    exception. If it validates, the we check the optional length of the string using 
    optional kwargs ``min_length`` et ``max_length``)
    
    :type value: string
    :param value: Value to validate.
    
    :type kwargs: any
    :param kwargs: Accepts all possible named arguments. If ``min_length`` or
                   ``max_length`` are set, they are used to validate the string length.
    """
    if not isinstance(value, basestring):
        raise ValidationError, 'invalid'
    value = value.strip()
    minlength_validator(len(value), **kwargs)
    maxlength_validator(len(value), **kwargs)

def integer_validator(value, **kwargs):
    """
    Validation of an integer
    
    Raises a `ValidationError` exception if it's not an integer'.
    
    :type value: string
    :param value: Value to validate. Receives a string becaus of the way ``input()`` works
                  but will be validated using ``int()``.
    
    :type kwargs: any
    :param kwargs: Accept all possible named arguments. If``min_length`` or
                   ``max_length`` are specified they are used to validate the value
                   within the limits set by the arguments.
    """
    try:
        int(value.strip())
    except (ValueError, TypeError), e:
        raise ValidationError, 'invalid'
    else:
        minlength_validator(value, **kwargs)
        maxlength_validator(value, **kwargs)

def choice_validator(value, **kwargs):
    """
    Validation of a choice selection
    
    Raises a `ValidationError` exception when the value does not correspond to an
    element in the available choices list .
    
    :type value: string
    :param value: Value to validate. Must correspond to an available element 
                  of choice.
    
    :type kwargs: any
    :param kwargs: Accept all possible named arguments. Must absolutely contain
                   the ``choices`` argument which is a ``tuple`` (or a list) containing
                   choices as a ``tuple`` (key, label) where  ``key`` is the element that
                   will be used to validate the value.
    """
    choices = kwargs['choices']
    choice_keys = []
    # Forces all keys to be a string
    for key,val in choices:
        if not isinstance(key, basestring):
            key = str(key)
        choice_keys.append(key)
    # Choice not in possible keys. Raises an exception
    if value.strip() not in choice_keys:
        raise ValidationError, 'invalid'

class BaseField(object):
    """
    Base field model
    
    The only default validation is if the input is not empty when it's mandatory
    """
    validators = []
    validators_context = {}
    error_messages = {
        'required': INPUT_REQUIRED_ERROR,
        'invalid': INPUT_INVALID_ERROR,
    }
    
    def __init__(self, label, required=False, default=None, can_retry=True, **kwargs):
        """
        :type label: string
        :param label: Label shown for the field
        
        :type required: string
        :param required: (optional) Indicates wether the field is mandatory. By default
                         a field never is (``False``).
        
        :type default: string
        :param default: (optional) Default value when the field is not filled.
                        Useless when the field is mandatory since it will be filled anyhow
                        By default, this argument is ``None``.
        
        :type can_retry: string
        :param can_retry: (optional) Indicates wether the field allows a retry for
                          an invalidated value. If unset, the field will raise an 
                          exception when the value is invalidated. If set, the field
                          will keep asking for a value that validates. By default
                          the option is set (``True``).
        
        :type kwargs: any
        :param kwargs: (optional) Accepts all possible named arguments.
        """
        self.label = label
        self.required = required
        self.can_retry = can_retry
        self._kwargs = kwargs
        self.errors = []
        self.default = default
        self.value = self.submitted_input = None
        
    def prompt(self):
        """
        Displays the input message and does the validation of the input
        
        :rtype: any
        :return: Returns the validated entered value.
        """
        try:
            self.submitted_input = raw_input(self.get_prompt_label(self.label))
        except UnicodeEncodeError:
            self.submitted_input = raw_input(self.get_prompt_label(self.label).encode('utf-8'))
        self.value = self.clean()
        
        return self.value
        
    def get_prompt_label(self, label):
        """
        Returns the field label with an indication if it is required
        
        :type label: string
        :param label: Label text
        
        :rtype: string
        :return: Label to display
        """
        if self.required:
            label += " (Required)"
        return label+" "
        
    def clean(self):
        """
        Validation, assignment of the input and retunrs the state of validation
        
        :rtype: any
        :return: Input that passed validators
        """
        self.errors = self.validate(self.submitted_input)
        self.errors += self.run_validators(self.submitted_input)
        
        if len(self.errors) > 0:
            return self.manage_error(self.errors)
        
        return self.submitted_input
        
    def manage_error(self, errors):
        """
        Validator errors management
        
        :type errors: list
        :param errors: List of errors received by the validators.
        
        :rtype: any
        :return: Returns  the input value validated
        """
        context = self._prepare_validator_context(self.submitted_input)
        d = {}
        if self.can_retry:
            print ', '.join([Template(item).safe_substitute(context) for item in errors]) + '.'
            return self.prompt()
        else:
            raise RequiredValue, msg

    def validate(self, value):
        """
        Check of an empty input and of the mandatory input mode
        
        :type value: any
        :param value: Input
        
        :rtype: list
        :return: List containing required field error message if input is empyt
                 otherwise, an empty list.
        """
        if value in EMPTY_VALUES and self.required:
            return [self.error_messages['required']]
        return []
        
    def _prepare_validator_context(self, value):
        """
        Method preparing kwargs passed to the validator
        
        :type value: any
        :param value: Input value
        
        :rtype: dict
        :return: Validator given field Instance specific context .
        """
        self.validators_context['show_value'] = value
        return self.validators_context

    def run_validators(self, value):
        """
        Runs all fields validators
        
        :type value: any
        :param value: Input value
        
        :rtype: list
        :return: Lists errors found by the validators if there were some.
        """
        if value in EMPTY_VALUES:
            return []
        errors = []
        context_kwargs = self._prepare_validator_context(value)
        for v in self.validators:
            try:
                v(value, **context_kwargs)
            except ValidationError, e:
                errors.append(self.error_messages[e[0]])
        return errors
        
    def render(self):
        """
        Renders the value
        
        :rtype: any
        :return: Defaults value when the field is not mandatory and input is
                 empty, otherwise, input value.
        """
        if self.value in EMPTY_VALUES:
            return self.default
        return self.value

class BooleanField(BaseField):
    """
    Boolean field though a yes/no input
    """
    validators = [boolean_validator]
    
    def __init__(self, label, default=True, choices_true=('y',), choices_false=('n',), **kwargs):
        """
        :type label: string
        :param label: Label displayed for the field
        
        :type default: bool
        :param default: (optional) Default value if the field is not filled.
                        True by default.
        
        :type choices_true: tuple or list
        :param choices_true: (optional) List of possible values to represent a
                             positive choice. By default, only one choice :``y``.
        
        :type choices_false: tuple or list
        :param choices_false: (optional) List of possible values to represent a
                              negative choice. By default, only one choice :``n``.
        
        :type kwargs: any
        :param kwargs: (optional) Accepts all possible named arguments.
        """
        self.choices_true = choices_true
        self.choices_false = choices_false
        super(BooleanField, self).__init__(label, default=default, **kwargs)
        
    def get_prompt_label(self, label):
        """
        Returns the field label with an indication if the field is mandatory
        
        Adds a list of possible values to represent a positive or negative choice
        
        :type label: string
        :param label: Label text
        
        :rtype: string
        :return: Label to be displayed
        """
        choices = list(self.choices_true)+list(self.choices_false)
        label += u" [%s]" % ', '.join(choices)
        return super(BooleanField, self).get_prompt_label(label)
        
    def _prepare_validator_context(self, value):
        """
        Method preparing the content of kwargs passed to each validator
        
        :type value: any
        :param value: Input value
        
        :rtype: dict
        :return: Validator given field Instance specific context.
        """
        context = super(BooleanField, self)._prepare_validator_context(value)
        context.update({
            'choices_true': self.choices_true,
            'choices_false': self.choices_false,
        })
        return context
        
    def render(self):
        """
         Renders the value

        :rtype: any
        :return: Defaults value when the field is not mandatory and input is
                 empty, otherwise, boolean representation of the value.
        """
        if self.value in self.choices_true:
            return True
        elif self.value in self.choices_false:
            return False
        else:
            return super(BooleanField, self).render()

class IntegerField(BaseField):
    """
    Integer numerical field
    """
    validators = [integer_validator]
    
    def __init__(self, label, default=0, min_length=None, max_length=None, **kwargs):
        """
        :type label: string
        :param label: Label displayed for the field
        
        :type default: int
        :param default: (optional) Default value when the field is not filled.
                        Bu default : ``0``.
        
        :type min_length: int
        :param min_length: (optional) Minimum possible value.
        
        :type max_length: int
        :param max_length: (optional) Maxiumum possible value.
        
        :type kwargs: any
        :param kwargs: (optional) Accepts all possible named arguments.
        """
        self.min_length = min_length
        self.max_length = max_length
        self.error_messages['min_length'] = INPUT_MINLENGTH_ERROR
        self.error_messages['max_length'] = INPUT_MAXLENGTH_ERROR
        super(IntegerField, self).__init__(label, default=default, **kwargs)
        
    def _prepare_validator_context(self, value):
        """
        Method preparing the content of kwargs passed to each validator

        :type value: any
        :param value: Input value

        :rtype: dict
        :return: Validator given field Instance specific context.
        """
        context = super(IntegerField, self)._prepare_validator_context(value)
        context.update({
            'min_length': self.min_length,
            'max_length': self.max_length,
        })
        return context
        
    def get_prompt_label(self, label):
        """
        Returns the field label with an indication if the field is mandatory
        
        Adds possible values limits when there are some.
        
        :type label: string
        :param label: Label text
        
        :rtype: string
        :return: Label to display
        """
        limits = []
        if self.min_length:
            limits.append("More than '%s'"%self.min_length)
        if self.max_length:
            limits.append("Less than %s"%self.max_length)
        if len(limits)>0:
            label += u" [%s]" % ', '.join(limits)
        return super(IntegerField, self).get_prompt_label(label)
        
    def render(self):
        """
        Renders the value

        :rtype: any
        :return: Defaults value when the field is not mandatory and input is
                 empty, otherwise, input value.
        """
        if self.value in EMPTY_VALUES:
            return self.default
        elif self.value != None:
            return int(self.value)
        return self.value

class StringField(BaseField):
    """
    Input field for a character string
    """
    validators = [string_validator]
    
    def __init__(self, label, default=None, min_length=None, max_length=None, **kwargs):
        """
        :type label: string
        :param label: Label displayed for the field
        
        :type default: string
        :param default: (optional) Default value when the field is not filled.
                        Default value : ``None``.
        
        :type min_length: int
        :param min_length: (optional) Minimal length for the character string
        
        :type max_length: int
        :param max_length: (optional) Maximal length for the character string
        
        :type kwargs: any
        :param kwargs: (optional) Accepts all possible named arguments.
        """
        self.min_length = min_length
        self.max_length = max_length
        self.error_messages['min_length'] = INPUT_MINCHARS_ERROR
        self.error_messages['max_length'] = INPUT_MAXCHARS_ERROR
        super(StringField, self).__init__(label, default=default, **kwargs)
        
    def _prepare_validator_context(self, value):
        """
        Method preparing the content of kwargs passed to each validator

        :type value: any
        :param value: Input value

        :rtype: dict
        :return: Validator given field Instance specific context.
        """
        context = super(StringField, self)._prepare_validator_context(value)
        context.update({
            'show_value': len(value),
            'min_length': self.min_length,
            'max_length': self.max_length,
        })
        return context
        
    def get_prompt_label(self, label):
        """
        Returns the field label with an indication if the field is mandatory

        Adds possible length limits when there are some.

        :type label: string
        :param label: Label text

        :rtype: string
        :return: Label to display
        
        """
        limits = []
        if self.min_length:
            limits.append('Min %s characters'%self.min_length)
        if self.max_length:
            limits.append('Max %s characters'%self.max_length)
        if len(limits)>0:
            label += u" [%s]" % ', '.join(limits)
        return super(StringField, self).get_prompt_label(label)

class ChoiceField(BaseField):
    """
    inpupt field for a value in a list of choices
    """
    validators = [choice_validator]
    
    def __init__(self, label, choices, input_label=None, default=None, **kwargs):
        """
        :type label: string
        :param label: Label displayed for the field
        
        :type choices: list
        :param choices: List of possible choices
        
        :type input_label: string
        :param input_label: (optional) Extra input label. This field, unlike the others
                            brings the cursor to the next line and not directly after the 
                            label that displays the list of choices. Bu default, when this
                            extra label is not set, input is just represented by a ``>``
                            at the beginning of the line. If the extra label is set, it 
                            will be placed right before this character 
        
        :type default: string
        :param default: (optional) Default value if the field is not set.
                        Default to``None``.
        
        :type kwargs: any
        :param kwargs: (optional) Accepts all possible named arguments.
        """
        self.choices = choices
        self.input_label = input_label
        super(ChoiceField, self).__init__(label, default=default, **kwargs)
        
    def _prepare_validator_context(self, value):
        """
        Method preparing the content of kwargs passed to each validator

        :type value: any
        :param value: Input value

        :rtype: dict
        :return: Validator given field Instance specific context.
        """
        context = super(ChoiceField, self)._prepare_validator_context(value)
        context.update({
            'choices': self.choices,
        })
        return context
        
    def get_prompt_label(self, label):
        """
        Returns the label with an indication if the field is mandatory
        
        Also prints the list of possible choices, with one  choice per line
        being the choice itself in brackets, followed by the value label and
        the input itself with its extra label : ::
        
            You are :
            * [male] A male
            * [female] A female
            * [alf] An alien from Melmac
            You choice>
        
        :type label: string
        :param label: Label text
        
        :rtype: string
        :return: Label to display
        """
        block = ''
        required = ''
        if self.required:
            required = " (Required)"
        if self.submitted_input == None:
            block += u"%s %s\n" % (label, required)
            for item in self.choices:
                block += u"* [%s] %s\n" % item
        if self.input_label:
            block += self.input_label+" "
        return block+"> "
        
#
if __name__ == "__main__":
    quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'
    print "(Quit programm with %s)" % quit_command
    try:
        ## BOOL
        #b = BooleanField(u"Test booléen :", required=True)
        #b.prompt()
        #print b.render()
        ## BOOL
        #b = BooleanField(u"Test booléen :", required=False)
        #b.prompt()
        #print b.render()
        ## INT
        #b = IntegerField("Test integer :", required=True)
        #b.prompt()
        #print b.render()
        ## INT
        #b = IntegerField("Test integer :", required=False, min_length=3, max_length=10)
        #b.prompt()
        #print b.render()
        ## STRING
        #b = StringField("Test string :", default="I'am empty.", required=True, min_length=3, max_length=10)
        #b.prompt()
        #print b.render()
        ## STRING
        #b = StringField("Test string :", default="I'am empty.", required=False)
        #b.prompt()
        #print b.render()
        # CHOICES
        b = ChoiceField("Test choices :", default="I'am empty.", required=False, choices=(
            (1, 'Coco Lapin !'),
            (2, u'Plôpïtix'),
            ('foo', u'FŒŒ'),
        ))
        b.prompt()
        print b.render()
        
    except KeyboardInterrupt:
        print
        print "You have aborted operations"
        sys.exit(0)
