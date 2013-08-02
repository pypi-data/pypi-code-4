# coding=utf-8
from django.forms import widgets

from django_helpers.helpers.views import render_to_string
from django_helpers.apps.static_manager import jQueryURL
from django_helpers.apps.forms.widgets import Widget


__author__ = 'ajumell'


class TinyMCEEditorOptions(object):
    pass


class TinyMCEWidget(Widget, widgets.Textarea):
    def __init__(self, *args, **kwargs):
        self.js_files = [jQueryURL, 'tiny_mce/tiny_mce.js', 'tiny_mce/jquery.tinymce.js']
        widgets.Textarea.__init__(self, *args, **kwargs)

    def render_js(self):
        return render_to_string('django-helpers/forms/tiny_mce.js', {
        })