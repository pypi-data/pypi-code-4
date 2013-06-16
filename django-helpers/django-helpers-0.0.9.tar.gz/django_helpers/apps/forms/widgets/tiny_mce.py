# coding=utf-8
from django_helpers.helpers.views import render_to_string
from django.forms import widgets
from django_helpers.templatetags.static_manger import add_js_file, require_jquery
from django_helpers.apps.forms.widgets import Widget

__author__ = 'ajumell'


class TinyMCEEditorOptions(object):
    pass


class TinyMCEWidget(Widget, widgets.Textarea):
    def __init__(self, *args, **kwargs):
        require_jquery()
        add_js_file('tiny_mce/tiny_mce.js')
        add_js_file('tiny_mce/jquery.tinymce.js')
        widgets.Textarea.__init__(self, *args, **kwargs)

    def render_js(self):
        return render_to_string('django-helpers/forms/tiny_mce.js', {
        })