from django import forms
from django.forms import widgets
from django.utils.safestring import SafeString
import logging

from ChAppliN import settings

logger = logging.getLogger('to-terminal')

class FancyRadioWidget(forms.HiddenInput):
    
    """ JavaScript version of a radio select. Contains a script tag with a
    JavaScript class (SEE "static/moreforms/fields.js") and a hidden input
    field, which is the current superclass.
    
    :param choices: A list of choices (see `choices` argument for
        django.forms.ChoiceField)
    """
    
    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices', None)
        super(FancyRadioWidget, self).__init__(*args, **kwargs)
        
    def render(self, *args, **kwargs):
        name = 'null'
        value = 'null'
        if 'name' in kwargs:
            name = kwargs['name']
        if 'value' in kwargs:
            value = kwargs['value']
            
        # Get the static url
        ext = ('%smoreforms/fields.js'%(settings.STATIC_URL))
                
        return SafeString("""
            <script type="text/javascript"
                src="%s"></script>
            <script>
                alert('Hello!');
                var select = FancyRadioSelect(
                    %s,     // name
                    %s,     // selected value
                    %s,     // javascript list of choices.
                );
                select.render();
            </script>
            %s
        """%(ext, name, value, self._js_choices(self.choices),
             super(FancyRadioWidget, self).render(*args, **kwargs))
        )
        
    def _js_choices(self, choices):
        _joined = []
        for choice in choices:
            _joined.append('new Array("%s")'%('","'.join(choice)))
        s = "new Array(%s)"%(', '.join(_joined))
        return s
    
class NoScriptRadioWidget(forms.RadioSelect):
    
    """ Basically, a RadioSelect wrapped in a <noscript></noscript> tag.
    
    :param choices: A list of choices (SEE django.forms.ChoiceField)
    """
    
    def __init__(self, *args, **kwargs):
        super(NoScriptRadioWidget, self).__init__(*args, **kwargs)
    
    def render(self, *args, **kwargs):
        return """
            <noscript>
                %s
            <noscript>
        """%(super(NoScriptRadioWidget, self).render(*args, **kwargs));
    

class FancyRadioMultiWidget(forms.MultiWidget):
    
    """A MultiWidget that combines FancyRadioWidget and NoScriptRadioWidget
    to be rendered onto the page.
    
    :param choices: a list of choices.
    """
    
    def __init__(self, *args, **kwargs):
        
        choices = kwargs.pop('choices', None)
        
        widgets = (
            FancyRadioWidget(choices=choices),
            NoScriptRadioWidget(choices=choices),
        )
        
        super(FancyRadioMultiWidget, self).__init__(widgets=widgets, *args, **kwargs)
    
    def decompress(self, value):
        if value:
            return [value, ]
        return [None, ]