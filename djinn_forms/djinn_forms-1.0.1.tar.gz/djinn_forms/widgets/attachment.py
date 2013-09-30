from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse


class AttachmentWidget(forms.widgets.Widget):

    """ Extended file widget, using the jquery file uploader. """

    def __init__(self, model, template, attrs=None):

        super(AttachmentWidget, self).__init__(attrs=attrs)

        self.model = model
        self.template = template

    def value_from_datadict(self, data, files, name):

        if self.attrs.get("multiple", False):
            return [int(val) for val in data.get(name, "").split(",") if val]
        else:
            return data.get(name, None)

    def _normalize_value(self, value):

        if self.attrs.get("multiple", False):
            if not hasattr(value, "__iter__"):
                value = [value]
            
            return filter(lambda x: self.model.objects.filter(pk=x).exists(), 
                          value)
        else:
            return value

    def render(self, name, value, attrs=None):

        value = self._normalize_value(value)

        context = {
            'name': name, 
            'button_label': self.attrs.get("button_label", ""),
            'widget': self,
            'show_progress': True,
            'multiple': False,
            'upload_url': reverse("djinn_forms_fileupload")
            }

        if self.attrs.get("multiple", False):
            context['value'] = ",".join([str(val) for val in value])
        else:
            context['value'] = value or ""

        attachments = []

        if value:
            if hasattr(value, "__iter__"):
                for val in value:
                    attachments.append(self.model.objects.get(pk=val))
            else:
                attachments.append(self.model.objects.get(pk=value))

        context['attachments'] = attachments
        context.update(self.attrs)
        
        if attrs:
            context.update(attrs)

        return mark_safe(render_to_string(self.template, context))
