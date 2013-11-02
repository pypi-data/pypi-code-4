from django import forms

class SubmitWidget(forms.Widget):
    
    """ Basically, a submit button.
    """
    
    def __init__(self, button_label, attrs=None):
        super(SubmitWidget, self).__init__(attrs)
        self.button_label = button_label
        self.label=None
        
    def render(self, *args, **kwargs):
        attrs = kwargs.pop('attrs', None)
        from django.utils.safestring import SafeString
        
        attrs_str = ''
        for k,v in attrs:
            attrs_str += '%s="%s"'%(k,v)
        return '<input type="submit" value="%s" %s'%(
                self.button_label,
                attrs_str )

class AutoSubmitWidget(forms.Widget):
    
    """Contains a JavaScript tag to automatically submit the parent
    form on a field change.
    """
    
    def __init__(self, *args, **kwargs):
        super(AutoSubmitWidget, self).__init__(*args, **kwargs)    
        
    def render(self, *args, **kwargs):
        attrs = kwargs.pop('attrs', None)
        return '''<script type="text/javascript">
    $("input[name='%s'").click(function(){
        $(this).closest("form").submit();
        });
    </script>\n'''%(attrs['name'])