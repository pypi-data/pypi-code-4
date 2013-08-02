import datetime

from django.core.urlresolvers import reverse
from django.db import router
from django.db.models import ForeignKey, Model
from django.forms.util import from_current_timezone
from django.utils import formats, six, datetime_safe
from django.utils.encoding import force_text

from django_helpers.apps.forms.widgets.bootstrap import bootstrap_date_format
from django_helpers.helpers.views import render_to_string
from django_helpers.utils.html import generate_code

from js_imports import require_date_filed

#
#   This app will require forms app for some widgets.
#

input_list = """
    text
    textarea
    select
    date
    datetime
    dateui
    combodate
    html5types
    checklist
    wysihtml5
    typeahead
    select2
"""


class BaseEditable(object):
    html_tag = 'a'
    class_names = None
    js_files = None
    css_files = None
    title = ''

    has_rendered = False
    editable = None
    field_name = None
    js_template = None

    def __init__(self, required=None):
        self.required = required

    def _load_validations_from_model(self):
        field = self.get_model_field()
        self.required = not field.blank
        # TODO: Add more validations.

    def get_model_field(self):
        editable = self.editable
        return editable.get_model_field(self.field_name)

    def get_model_field_type(self):
        editable = self.editable
        return editable.get_model_field_type(self.field_name)

    def render(self):
        editable = self.editable
        if editable is None:
            raise

        self.has_rendered = True
        name = self.field_name
        field_id = editable.get_id(name)
        value = editable.get_value(name)
        text = self.to_string(value)
        attrs = {
            'id': field_id
        }
        if self.html_tag == 'a':
            attrs['href'] = '#'

        return generate_code(self.html_tag, attrs, text)

    def render_js(self):
        data = self.generate_render_data()
        return render_to_string(self.js_template, data)

    def __unicode__(self):
        return self.render()

    def __str__(self):
        return self.render()

    def __repr__(self):
        return self.render()

    def get_id(self):
        name = self.field_name
        return self.editable.get_id(name)

    def generate_render_data(self):
        editable = self.editable
        return {
            'pk': editable.pk,
            'title': self.title,
            'name': self.field_name,
            'field_id': self.get_id(),
            'save_url': reverse(editable.editable_id + "_save")
        }

    def to_python(self, value):
        """
        This function will handle the convertion of the
        string to its corresponding python object.
        @param value: The string value given from the http post
        @return: the converted value. In normal cases it will be same.
        """
        return value

    def to_string(self, value):
        """
        This function will convert the python object to
        the string representation
        @param value: python object
        @return: string representation of the python object
        """
        return value


class TextEditable(BaseEditable):
    placeholder = ''
    clear = True
    js_template = 'x-editable/text.js'

    def generate_render_data(self):
        data = BaseEditable.generate_render_data(self)
        data['placeholder'] = self.placeholder
        data['clear'] = self.clear
        return data


class TextAreaEditable(TextEditable):
    rows = 7
    js_template = 'x-editable/textarea.js'

    def generate_render_data(self):
        data = TextEditable.generate_render_data(self)
        data['rows'] = self.rows
        return data


class SelectEditable(BaseEditable):
    source_cache = True
    source_error = "Error occured when loading data."
    prepend = False
    source = None


class BaseTemporalField(TextEditable):
    date_format = None

    def to_python(self, value):
        # Model cannot handle the conversion since it does not
        # know the format.
        unicode_value = force_text(value, strings_only=True)
        if isinstance(unicode_value, six.text_type):
            value = unicode_value.strip()

        if isinstance(value, six.text_type):
            try:
                return self.strptime(value, self.date_format)
            except (ValueError, TypeError):
                raise
        raise Exception('Invalid format')

    # noinspection PyShadowingBuiltins
    def strptime(self, value, format):
        field_type = self.get_model_field_type()
        val = datetime.datetime.strptime(value, format)
        if field_type == 'DateField':
            val = val.date()
        elif field_type == 'TimeField':
            val = val.time()
        else:
            val = from_current_timezone(val)
        return val

    def to_string(self, value):
        if hasattr(value, 'strftime'):
            value = datetime_safe.new_datetime(value)
            return value.strftime(self.date_format)
        return value


class DatePickerEditable(BaseTemporalField):
    js_template = 'x-editable/date.js'
    js_files = require_date_filed()

    def __init__(self, date_format=None, view_format=None):
        TextEditable.__init__(self)

        if date_format is None:
            date_format = formats.get_format('DATE_INPUT_FORMATS')[0]

        if view_format is None:
            view_format = date_format

        self.date_format = date_format
        self.view_format = view_format

    def generate_render_data(self):
        data = TextEditable.generate_render_data(self)
        data['date_format'] = bootstrap_date_format(self.date_format)
        data['view_format'] = bootstrap_date_format(self.view_format)
        return data


class BaseChoiceField(BaseEditable):
    def __init__(self, required=None, choices=None, queryset=None):
        BaseEditable.__init__(self, required)
        self.choices = choices
        self.queryset = queryset

    def _get_choices(self):
        choices = self.choices
        queryset = self.queryset

        model_field = self.get_model_field()

        if choices is None and queryset is None:
            # Find if model has relation or choices
            is_foreign = isinstance(model_field, ForeignKey)
            if not is_foreign:
                # Borrowed from the django code base.
                choices = model_field.choices
                self.choices = choices
                return choices
            else:
                # Borrowed from the django code base.
                # django/db/models/fields/related.py Line 1088, v:1.5.1
                # TODO Find a method to implement using multiple db.
                queryset = model_field.rel.to._default_manager.using(None).complex_filter(model_field.rel.limit_choices_to),
                if type(queryset) is tuple and len(queryset) == 1:
                    queryset = queryset[0]
                self.queryset = queryset
                return queryset
        elif choices is None and queryset is not None:
            return queryset
        elif choices is not None and queryset is None:
            return choices
        else:
            raise

    def list(self):
        result = []
        choices = self._get_choices()
        for choice in choices:
            if type(choice) == tuple:
                pk = choice[0]
                value = choice[1]
            elif isinstance(choice, Model):
                pk = choice.pk
                value = str(choice)
            else:
                raise Exception('Instance is an instance of %s not Model. ' % type(choice) + str(choice))

            result.append({
                'value': pk,
                'text': value
            })
        return result

    def generate_render_data(self):
        editable = self.editable
        data = BaseEditable.generate_render_data(self)
        data['source'] = reverse(editable.editable_id + "_list", kwargs={
            'field_name': self.field_name
        })
        return data


class SimpleSelectField(BaseChoiceField):
    js_template = 'x-editable/select.js'


class ModelSelectField(SimpleSelectField):
    def to_python(self, value):
        field = self.get_model_field()
        editable = self.editable
        model_instance = editable.get_instance()
        using = router.db_for_read(model_instance.__class__, instance=model_instance)
        qs = field.rel.to._default_manager.using(using).filter(
            **{field.rel.field_name: value}
        )
        return qs.complex_filter(field.rel.limit_choices_to)[0]

    def to_string(self, value):
        return unicode(value)
