from django import forms
from pml.forms import widgets

class PMLBaseField(object):
    def __init__(self, *args, **kwargs):
        super(PMLBaseField, self).__init__(*args, **kwargs)
        self.widget.label = self.label
        self.widget.help_text = self.help_text

class PMLCheckBoxField(PMLBaseField, forms.ChoiceField):
    widget = widgets.PMLCheckBoxWidget


class PMLRadioField(PMLBaseField, forms.ChoiceField):
    widget = widgets.PMLRadioWidget

    
class PMLSelectField(PMLBaseField, forms.ChoiceField):
    widget = widgets.PMLSelectWidget


class PMLTextField(PMLBaseField, forms.CharField):
    widget = widgets.PMLTextWidget


class PMLHiddenField(PMLTextField):
    widget = widgets.PMLHiddenWidget
