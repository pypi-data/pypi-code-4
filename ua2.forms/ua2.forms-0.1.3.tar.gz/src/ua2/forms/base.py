import warnings
from django import forms
from django.template import Context, loader


class BaseForm(object):
    _ref_class = None

    def __init__(self, *kargs, **kwargs):
        """
        Init accept two additional arguments:
        request - http request from view
        template - optional template name
        """
        assert self._ref_class is not None

        self._request = kwargs.pop('request', None)
        self._template = kwargs.pop('template', None)

        super(self._ref_class, self).__init__(*kargs, **kwargs)

        init = getattr(self, 'init', None)
        if callable(init):
            warnings.warn("Calling init method is Depricated. Please use overload __init__ method", DeprecationWarning)
            init()

    @property
    def request(self):
        return self._request

    def get_value_for(self, field_name):
        """ used to obtain value of fields

            useful when need get value not depend on form state
        """
        if self.is_bound:
            return self[field_name].data
        return self.initial.get(field_name, self.fields[field_name].initial)

    def get_template_name(self):
        return self._template or "ua2.forms/form.html"

    def output_via_template(self):
        "Helper function for fieldsting fields data from form."
        bound_fields = [forms.forms.BoundField(self, field, name) for name, field \
                        in self.fields.items()]

        c = Context(dict(form = self, bound_fields = bound_fields))
        t = loader.get_template(self.get_template_name())
        return t.render(c)


    def as_template(self):
        "{{ form.as_template }}"
        for field in self.fields.keys():
            self.fields[field].str_class = str(self.fields[field].widget.__class__.__name__)
        return self.output_via_template()


    def populate(self, field_name, queryset, add_empty=False, label_name=None,
                 value_name=None, empty_label=None, empty_value=None):
        """ Pupulate chouice field by given QuerySet
        Args:
            field_name: field name in form (as string)
            queryset: QierySet object
            add_empty: if set to True function prepend list of
                choices by empty line
            label_name: name of field, propery or method in queryset
                instance model, that will be set as label in dropdown
            value_name: name of field, propery or method in queryset
                instance model, that will be set as value in dropdown
            empty_label: value, that will be set for empty line,
                by defaylt it set to '-------'
            empty_value: value, that will be set for empty line,
                by default it set to ''

        """
        field = self.fields[field_name]

        field.choices = []
        if add_empty:
            field.choices.append((empty_label or '',
                                  empty_value or '-------'))
