from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


class ImageWidget(forms.widgets.Widget):

    """ Image upload widget """

    template_name = "djinn_forms/snippets/imagewidget.html"

    def render(self, name, value, attrs=None):

        context = {
            'name': name, 
            'widget': self,
            'show_progress': True,
            'multiple': False,
            'value': value
            }

        context.update(self.attrs)
        
        if attrs:
            context.update(attrs)

        return mark_safe(render_to_string(self.template_name, context))
