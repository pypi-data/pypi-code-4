# coding=utf-8
__author__ = 'ajumell'

import types
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.utils.safestring import mark_safe
from django_helpers.templatetags.jsmin import remove_blank_lines

from django_helpers.helpers.views import render_to_string

from preprocessors.replace_widgets import replace_widgets
from preprocessors.validation import validation_preprocessor, remote_validation_preprocessor
from preprocessors.extra_attrs import extra_widget_args, extra_widget_class_names
from exceptions import CSRFTokenMissingException, FormIDMissingException


def get_function(path):
    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' % (module, e))
    try:
        func = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" callable processor' % (module, attr))
    return func


class FormRenderer(object):
    # Text for the submit button
    form_submit = 'Submit'

    # If focus_first is set to True then the
    # first input element will be focused using js
    focus_first = None

    # A Unique identifier for this form
    form_id = None

    # Name of the template to be rendered.
    template = 'form-renderer/form.html'

    # Method of the form
    method = 'POST'

    # URL (not name of the url) to which this form has to be submitted.
    form_action = ''

    # Extra context dict
    extra_context_dict = None

    # A set of functions which will be executed when render function is called.
    # The form renderer will be passed as a parameter to this function
    pre_processors = [
        validation_preprocessor,
        remote_validation_preprocessor,
        extra_widget_args,
        extra_widget_class_names,
        replace_widgets
    ]

    # A list of extra templates that has to be loaded.
    # This helps pre processors to add code to template.
    extra_templates = []

    def __init__(self, form, request=None, form_id=None, csrf_token=None, template=None):
        self.form = form
        self.request = request
        self.csrf_token = csrf_token

        if template is not None:
            self.template = template

        if self.request is None and csrf_token is None:
            raise CSRFTokenMissingException()

        if self.pre_processors is not None:
            self.pre_processors = self.pre_processors[:]

        if self.extra_templates is None:
            self.extra_templates = []
        else:
            self.extra_templates = self.extra_templates[:]

        if form_id is not None:
            self.form_id = form_id

    def __str__(self):
        return self.render()

    def __unicode__(self):
        return self.render()

    def render(self):
        if self.form_id is None:
            raise FormIDMissingException()

        pre_processors = self.pre_processors
        if pre_processors is not None:
            for pre_processor in pre_processors:
                if not isinstance(pre_processor, types.FunctionType):
                    pre_processor = get_function(pre_processor)

                if isinstance(pre_processor, types.FunctionType):
                    pre_processor(self)

        data = {
            'form': self.form,
            'form_submit': self.form_submit,
            'focus_first': self.focus_first,
            'form_id': self.form_id,
            'method': self.method,
            'form_action': self.form_action,
            'csrf_token_html': self.csrf_token
        }

        if type(self.extra_context_dict) is dict:
            data.update(self.extra_context_dict)

        templates = self.extra_templates[:]
        templates.insert(0, self.template)
        output = []
        for template in templates:
            output.append(render_to_string(template, data, self.request))
        return mark_safe(remove_blank_lines('\n'.join(output)))
