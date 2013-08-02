# coding=utf-8
import types

from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django_helpers.utils.html import generate_code


__author__ = 'ajumell'
__all__ = ('prepend_preprocessor', 'append_preprocessor')


def make_addon(text):
    return u'<span class="add-on">%s</span>' % conditional_escape(text)


def get_btn_class(color):
    if color != '':
        color = ' btn-' + color
    return 'btn' + color


def get_contents(text, icon):
    if icon != '':
        icon = generate_code('i', {
            'class': 'icon icon-' + icon
        }, '')
    return mark_safe(icon + conditional_escape(text))


def make_button(text, color='', button_type='button', icon=''):
    return generate_code('button', {
        'class': get_btn_class(color),
        'type': button_type
    }, get_contents(text, icon))


def make_link_button(text, url='#', color='', icon=''):
    return generate_code('a', {
        'class': get_btn_class(color),
        'href': url
    }, get_contents(text, icon))


def make_text(prop):
    name = 'addon'
    args = prop

    if isinstance(prop, dict):
        assert len(prop.keys()) == 1, 'There cannot be more than one property'
        name, args = prop.items()[0]

    elif type(prop) in (tuple, list):
        name = prop[0]
        args = prop[1:]
        assert len(args) > 0, 'Arguments must be greater than one'

    name = 'make_%s' % name
    if name not in globals():
        return

    func = globals()[name]

    if isinstance(func, types.FunctionType):
        if type(args) in (tuple, list):
            return func(*args)
        elif type(args) is dict:
            return func(**args)
        else:
            return func(args)


def _base_preprocessor(renderer, property_name='addend'):
    form = renderer.form
    datas = getattr(renderer, '%ss' % property_name, None)
    if type(datas) is not dict:
        return
    for name, data in datas.items():
        field = form.fields[name]
        setattr(field, 'has_%s' % property_name, True)
        if type(data) in (list, tuple):
            text = ''
            for prop in data:
                text += make_text(prop)
        else:
            text = make_text(data)
        setattr(field, '%s_text' % property_name, mark_safe(text))


def prepend_preprocessor(renderer):
    return _base_preprocessor(renderer, 'prepend')


def append_preprocessor(renderer):
    return _base_preprocessor(renderer, 'append')