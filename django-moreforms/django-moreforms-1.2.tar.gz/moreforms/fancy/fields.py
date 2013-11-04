from django import forms
from widgets import *

class FancySelectField(forms.ChoiceField):
    
    """ Represents a JavaScript-dependent radio input.
    
    :param choices: Choices to be rendered.
    """
    
    def __init__(self, *args, **kwargs):
        choices = kwargs['choices']
        super(FancySelectField, self).__init__(
            widget = FancyRadioMultiWidget(choices=choices),
            *args,
            **kwargs )
        
class SimpleSelectField(forms.Field):
    
    """ Like FancySelectField, but it renders a simple radio select widget
    for those who block JavaScript.
    
    :param choices: choices to be used for the widget.
    """
    
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        widget = NoScriptRadioWidget(choices=choices)
        super(SimpleSelectField, self).__init__(widget = widget, *args,
                                                **kwargs)

class FancyChoiceMultiField(forms.MultiValueField):
    
    def __init__(self, *args, **kwargs):
        
        choices = kwargs.pop('choices', None)
        
        fields = ( FancySelectField(choices=choices),
                  SimpleSelectField(choices=choices) )
        
        super(FancyChoiceMultiField, self).__init__(fields=fields,
            widget=FancyRadioMultiWidget(choices=choices), *args, **kwargs)
        
    def compress(self, data_list):
        return ','.join(data_list)
        
class FancyYesNo(FancyChoiceMultiField):
    
    def __init__(self, *args, **kwargs):
        choices = (
            ('y', 'Yes'),
            ('n', 'No'),
        )
        super(FancyYesNo, self).__init__(choices=choices, *args, **kwargs)