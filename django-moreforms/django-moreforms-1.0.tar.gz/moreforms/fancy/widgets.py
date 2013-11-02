from django import forms
from django.forms import widgets

class FancyRadioWidget(forms.RadioSelect):
    
    def __init__(self, *args, **kwargs):
        super(FancyRadioWidget).__init__(*args, **kwargs)
        
    def render(self, *args, **kwargs):
        name = kwargs.pop('name', None)
        value = kwargs.pop('value', None)
        #attrs = kwargs.pop('attrs', None)
        choices = kwargs.pop('choices', None)
        
        return """
            <script>
                var select = FancyRadioSelect(
                    %s,     // name
                    %s,     // selected value
                    %s,     // javascript list of choices.
                );
                select.render();
            </script>
        """%(name, value, self._js_choice(choices))
        
    def _js_choices(self, choices):
        _joined = []
        for choice in choices:
            _joined.append('["%s"]'%('","'.join(choice)))
        s = "[%s]"%(', '.join(_joined))
        return s
    

class FancyRadioSelect(forms.MultiWidget):
    
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', None)
        
        widgets = (
            FancyRadioWidget(choices=choices),
            forms.HiddenInput(),
            forms.RadioSelect(choices=choices),
        )
        
        super(FancyRadioSelect, self).__init__(
            widgets=widgets, *args, **kwargs)
    
    def decompress(self, value):
        if value:
            return [value, ]
        return [None, ]