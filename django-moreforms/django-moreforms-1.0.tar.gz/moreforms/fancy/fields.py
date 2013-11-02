from django import forms
from widgets import FancyRadioSelect

class FancyChoiceInput(forms.ChoiceField):
    
    def __init__(self, choices, *args, **kwargs):
        super(FancyChoiceInput, self).__init__(
            choices = choices,
            widget=FancyRadioSelect(choices),
            *args,
            **kwargs
        )

class FancyChoice(forms.MultiValueField):
    
    """A field that contains both javascript code and non-js code to render
    a tabular selection input field. If no javascript is present, the widget
    will be rendered as a radio field.
    
    :param choices: An iterable of choices.
        SEE django.forms.ChoiceField.choices.
        
    """
    
    def __init__(self, choices, *args, **kwargs):
        fields = (
            FancyChoiceInput(choices=choices),
            forms.HiddenInput(), )
        
        super(FancyChoice, self).__init__(
            fields=fields,
            widget = FancyRadioSelect(choices=choices),
            *args,
            **kwargs )
        
    def compress(self, data_list):
        return ','.join(data_list)
        
class FancyYesNo(FancyChoice):
    
    def __init__(self, *args, **kwargs):
        choices = (
            ('y', 'Yes'),
            ('n', 'No'),
        )
        super(FancyYesNo, self).__init__(choices=choices, *args, **kwargs)