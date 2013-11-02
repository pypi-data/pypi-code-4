from widgets import *
from django import forms

class SubmitInput(forms.Field):
    
    def __init__(self, label):
        super(SubmitInput, self).__init__(
            widget=SubmitWidget(label), required=False)
        self.label = ''
    
class AutoSubmitField(forms.Field):
    
    def __init__(self, *args, **kwargs):
        super(AutoSubmitField, self).__init__(
            widget=AutoSubmitWidget(),
            required=False, *args, **kwargs)
        self.label=''