from django import forms
from django.http import HttpRequest
import re, logging
logger = logging.getLogger('to_terminal')

class SimpleYesNoWidget(forms.widgets.RadioSelect):

    def __init__(self):
        super(SimpleYesNoWidget, self).__init__(
                choices = (('y', 'Yes'), ('n', 'No')))

class FancySelect(forms.MultiWidget):

    choices = ()
    maximum_select = 0
    preselected= ()
    selected_input = forms.HiddenInput(attrs={
        'name': 'selection',
        'id' : 'selection',
    });

    def __init__(self, choices, maximum_select=0, preselected=()):
        self.choices = choices
        self.maximum_select = maximum_select
        self.preselected = preselected
        super(FancySelect, self).__init__(widgets=(
            self.selected_input,
        ))

    def render(self, name, value, attrs=None):
        s = """
<script type="text/javascript">
        ('%s').click(updateFancyInput('%s', %d));
</script>"""%(name, self.maximum_select, name)
        s += """<table id="%s" class="requires-js fancy-checkbox">
            <tr>"""%(name)
        for choice in self.choices:
            selected = ''
            if choice[0] in self.preselected:
                selected = 'selected'
            s += '<td id="%s" class="%s">%s</td>\n'%(
                    choice[0], selected, choice[1])
        s += "</tr>"
        s += self.selected_input.render(name, value, attrs)
        s += "</table>\n"

        return s


    def decompress(self, value):
        if value:
            return value
        return None

class FancyYesNoWidget(FancySelect):

    def __init__(self):
        super(FancyYesNoWidget, self).__init__(
                (('y', 'Yes'),
                 ('n', 'No') ),
                maximum_select = 1,
                preselected = 'n')

class YesNoSelect(forms.Field):

    def __init__(self, javascript=False, *args, **kwargs):
        if javascript:
            self.widget = FancyYesNoWidget()
        else:
            self.widget = SimpleYesNoWidget()
        super(YesNoSelect, self).__init__(*args, **kwargs)

    def clean(self):
        pass