# coding=utf-8
__author__ = 'ajumell'

from django_helpers import get_settings_val
from django_helpers.helpers.templatetags import TemplateNode, parse_args
from django.contrib.staticfiles import finders
from django import template
from django.conf import settings
register = template.Library()

JS_FILES = []
CSS_FILES = []

STATIC_URL = get_settings_val('STATIC_URL')
INCLUDE_CSS = get_settings_val('STATIC_MANAGER_INCLUDE_CSS', True)
INCLUDE_JS = get_settings_val('STATIC_MANAGER_INCLUDE_JS', True)

__all__ = ('add_js_file', 'add_css_file', 'require_jquery', 'require_jquery_ui', 'require_bootstrap')


class StaticFileNotFoundException(Exception):
    def __init__(self, name):
        Exception.__init__(self, 'Static File "%s" not found.' % name)


def add_file(array, name):
    if array.count(name) == 0:
        if finders.find(name) is None:
            if getattr(settings, 'RAISE_STATIC_EXCEPTIONS', True):
                raise StaticFileNotFoundException(name)
            else:
                print StaticFileNotFoundException(name)
        else:
            array.append(name)


def add_js_file(name, force=False):
    if INCLUDE_JS or force:
        add_file(JS_FILES, name)


def add_css_file(name, force=False):
    if INCLUDE_CSS or force:
        add_file(CSS_FILES, name)

# TODO: Find a method to make this to one file
# TODO: Check absolute urls in included files

def get_code(template, array):
    code = []
    for f in array:
        if f.startswith("http://") or f.startswith("https://"):
            s = ""
        else:
            s = STATIC_URL
        code.append(template % (s, f))
    return '\n'.join(code)


def get_js_code():
    return get_code('<script type="text/javascript" src="%s%s"></script>', JS_FILES)


def get_css_code():
    return get_code('<link rel="stylesheet" href="%s%s" />', CSS_FILES)


class StaticFilesNode(TemplateNode):
    def render(self, context):
        mode = 'all'
        if len(self.args) > 0:
            mode = self.args[0].resolve(context, True)
            if mode not in ['css', 'js']:
                mode = 'all'

        if mode == 'all':
            return get_css_code() + '\n' + get_js_code()

        if mode == 'css':
            return get_css_code()

        if mode == 'js':
            return get_js_code()


@register.tag
def static_files(parser, token):
    bits = token.contents.split()
    args, kwargs = parse_args(bits, parser)
    return StaticFilesNode(args, kwargs)


def require_jquery():
    add_js_file('django-helpers/js/jquery-1.7.1.min.js')


def add_jquery_easing():
    add_js_file('django-helpers/js/jquery.easing.min.js')


def require_jquery_ui():
    add_js_file('django-helpers/js/jquery-ui.js')


def require_bootstrap():
    require_jquery()
    add_js_file('django-helpers/bootstrap/js/bootstrap.min.js')

    add_css_file('django-helpers/bootstrap/css/bootstrap.min.css')
    add_css_file('django-helpers/bootstrap/css/bootstrap-responsive.min.css')
