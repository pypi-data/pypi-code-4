from django_helpers.apps.static_manager import jQueryURL
from django_helpers.helpers.views import render_to_string

__author__ = 'ajumell'

import os

from django import template

from django.contrib.staticfiles import finders

from django_helpers import get_settings_val

from ..exceptions import AppNameMissingException
from ..storage import get_files
from ..utils import add_js_from_context, resolve_file_name, generate_js_from_context

STATIC_URL = get_settings_val('STATIC_URL')
_IS_DEBUG = get_settings_val('DEBUG', True)
SAVE_FILE = get_settings_val('STATIC_MANAGER_MAKE_FILE', True)
register = template.Library()


def get_path(path):
    dirs = get_settings_val('STATICFILES_DIRS')
    if len(dirs) is 0:
        return

    root = dirs[0]
    root = os.path.abspath(root)

    if not os.path.exists(root):
        raise Exception('%s does not exists.' % root)

    new_path = os.path.join(root, path)
    if os.path.exists(new_path):
        return new_path

    new_path = root
    parts = os.path.split(path)
    name = parts[-1]
    parts = parts[:-1]
    for part in parts:
        new_path = os.path.join(new_path, part)
        if os.path.exists(new_path):
            if not os.path.isdir(new_path):
                raise
        else:
            os.mkdir(new_path)
    new_path = os.path.join(new_path, name)
    return new_path


def save_file(path, array):
    if not SAVE_FILE:
        return

    path = get_path(path)
    if path is None:
        return

    contents = ''
    for file_name in array:
        file_name = resolve_file_name(file_name)
        real = finders.find(file_name)
        if real is None:
            raise Exception('File %s not found.' % file_name)
        fp = file(real)
        contents += fp.read()
        fp.close()
    fp = file(path, 'w')
    fp.write(contents)
    fp.close()


def _render_code(files, template):
    code = []
    for f in files:
        f = unicode(f)
        if f.startswith("http://") or f.startswith("https://"):
            s = ""
        else:
            s = STATIC_URL
        code.append(template % (s, f))
    return '\n'.join(code)


def has_ajax_rendering(context):
    return 'ajax_block_register' in context


def resolve_app_name(context, app_name):
    if app_name is None:
        if 'app_name' not in context:
            raise AppNameMissingException()
        else:
            return context['app_name']
    elif app_name in ['js', 'css', 'all']:
        raise
    return app_name


@register.simple_tag(takes_context=True)
def static_files(context, app_name=None, file_type='js'):
    if file_type == 'js':
        return js_files(context, app_name)
    elif file_type == 'css':
        return css_files(context, app_name)
    else:
        raise


@register.simple_tag(takes_context=True)
def render_js(context, app_name=None):
    op = generate_js_from_context(context, app_name)
    if has_ajax_rendering(context):
        static_url = get_settings_val('STATIC_URL')
        if app_name is None:
            raise

        for block in op:
            files = block['files']
            url = static_url + jQueryURL
            while url in files:
                files.remove(url)

        generated_code = render_to_string('static-manager/render-js.html', {
            'code_blocks': op,
            'STATIC_URL': static_url,
            'app_name': app_name
        })
    else:
        generated_code = '<script type="text/javascript">'
        for block in op:
            generated_code += block['js_code']
    return generated_code + '</script>'


@register.simple_tag(takes_context=True)
def js_files(context, app_name=None):
    app_name = resolve_app_name(context, app_name)
    add_js_from_context(context, app_name)
    if has_ajax_rendering(context):
        return render_js(context, app_name)
    else:
        files = get_files('js', app_name)
        template = '<script type="text/javascript" src="%s%s"></script>'
        return _render_code(files, template) + render_js(context, app_name)


@register.simple_tag(takes_context=True)
def css_files(context, app_name=None):
    app_name = resolve_app_name(context, app_name)
    files = get_files('css', app_name)
    template = '<link rel="stylesheet" href="%s%s" />'
    return _render_code(files, template)
