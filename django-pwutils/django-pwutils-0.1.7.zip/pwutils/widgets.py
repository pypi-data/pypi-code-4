# -*- coding: utf-8 -*-
import logging

from django.forms import fields
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.forms.widgets import Select
from django.template.loader import render_to_string
from django.template import Context
from django import forms
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class AutoCompleteTextInput(fields.TextInput):
    class Media:
        css = {
            'all': ('css/jquery.autocomplete.css',)
        }
        js = (
            'js/jquery-1.4.2.min.js',
            'js/lib/jquery.bgiframe.min.js',
            'js/lib/jquery.ajaxQueue.js',
            'js/jquery.autocomplete.js'
        )

    def __init__(self, attrs=None, **kwargs):
        attrs = attrs or {}
        multiple = attrs.pop('multiple', False)
        super(AutoCompleteTextInput, self).__init__(attrs)
        self.multiple = multiple and 'true' or 'false'
        self.choices_url = kwargs.pop('choices_url', '')
        self.related_field = kwargs.pop('related_field', '')

    def render(self, name, value, attrs=None):
        output = super(AutoCompleteTextInput, self).render(name, value, attrs)

        if self.choices_url:
            choices = simplejson.dumps(reverse(str(self.choices_url)),
                                       ensure_ascii=False)
        else:
            choices = simplejson.dumps(self.choices, ensure_ascii=False)

        extra = ''
        if self.related_field:
            extra = u''',
                extraParams: {
                   %s: function() { return $("#id_%s").val(); }
                   }''' % (self.related_field, self.related_field)

        return output + mark_safe(u'''<script type="text/javascript">
            jQuery("#id_%s").autocomplete(%s, {
                width: 150,
                highlight: false,
                multiple: %s,
                multipleSeparator: ", ",
                scroll: true,
                scrollHeight: 300,
                matchContains: true,
                autoFill: true%s
            });
            </script>''' % (name, choices, self.multiple, extra))


class AutoCompleteCharField(fields.CharField):

    widget = AutoCompleteTextInput

    def __init__(self, choices=(), *args, **kwargs):

        super(AutoCompleteCharField, self).__init__(*args, **kwargs)

        self._choices = choices

    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        # Setting choices also sets the choices on the widget.
        # choices can be any iterable, but we call list() on it because
        # it will be consumed more than once.
        self._choices = self.widget.choices = list(value)

    choices = property(_get_choices, _set_choices)


class TemplateRadioSelect(Select):

    def __init__(self, template, *args, **kwargs):

        self.template = template
        self.request = kwargs.pop('request', None)
        super(TemplateRadioSelect, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, choices=()):
        logger.debug('template render %s %s' % (name, value))
        context = {'name': name,
                   'value': value,
                   'rendered_value': super(TemplateRadioSelect,
                                           self).render(name,
                                                        value,
                                                        attrs, choices),
                   'choices': self.choices,
                   'request': self.request,
                  }
        attrs.update(context)

        return mark_safe(render_to_string(self.template,
                                          context_instance=Context(attrs)))


CLIENT_CODE = """
<input type="text" name="%s_text" id="%s_text"/>
<input type="hidden" name="%s" id="%s" value="" />
<script type="text/javascript">
  $(function(){
    function formatItem(row) {
      return row[1] ;
    };
    function formatResult(row) {
      return row[1];
    };
    $("#%s_text").autocomplete('%s', {
      mustMatch: true,
      formatItem: formatItem,
      formatResult: formatResult
    });
    $("#%s_text").result(function(event, data, formatted) {
      $("#%s").val(data[0]);
    });
  });
</script>
"""


class ModelAutoCompleteWidget(forms.widgets.TextInput):
    """ widget autocomplete for text fields
    """
    html_id = ''

    def __init__(self, lookup_url=None, *args, **kwargs):
        super(forms.widgets.TextInput, self).__init__(*args, **kwargs)
        # url for Datasource
        self.lookup_url = lookup_url

    def render(self, name, value, attrs=None):
        if value == None:
            value = ''
        html_id = attrs.get('id', name)
        self.html_id = html_id
        lookup_url = self.lookup_url

        return mark_safe(CLIENT_CODE % (name, html_id, name, html_id, html_id,
                                        lookup_url, html_id, html_id))

    def value_from_datadict(self, data, files, name):
        """Given a dictionary of data and this widget's name, returns the value
           of this widget. Returns None if it's not provided.
        """
        return data.get(name, None)


class ModelAutoCompleteField(forms.fields.CharField):
    """Autocomplete form field for Model Model
    """
    model = None
    url = None

    def __init__(self, model,  lookup_url, *args, **kwargs):
        self.model, self.url = model, lookup_url
        super(ModelAutoCompleteField, self).__init__(
            widget=ModelAutoCompleteWidget(lookup_url=self.url),
            max_length=255, *args, **kwargs)

    def clean(self, value):
        try:
            obj = self.model.objects.get(pk=value)
        except self.model.DoesNotExist:
            raise ValidationError(u'Invalid item selected')
        return obj
