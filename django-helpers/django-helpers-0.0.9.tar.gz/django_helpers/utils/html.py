# coding=utf-8
from django.forms.util import flatatt
from django.utils.html import format_html
from django.utils.safestring import mark_safe


def get_class_names(class_names):
    if type(class_names) in (list, tuple):
        class_names = ' '.join(class_names)
    class_names = class_names.strip()
    while class_names.find('  ') > 0:
        class_names = class_names.replace('  ', '')
    return class_names


def generate_code(tag, attrs, text='', self_closing=False, start_only=False):
    class_names = attrs.pop('class')

    if class_names is not None:
        attrs['class'] = get_class_names(class_names)

    for key, val in attrs.items():
        if val is None:
            del attrs[key]

    attrs = flatatt(attrs)
    if self_closing:
        string = "<{0}{1} />"
        html = format_html(string, tag, attrs)
    elif start_only:
        string = "<{0}{1}>"
        html = format_html(string, tag, attrs)
    else:
        string = "<{0}{1}>{2}</{0}>"
        html = format_html(string, tag, attrs, text)
    return html