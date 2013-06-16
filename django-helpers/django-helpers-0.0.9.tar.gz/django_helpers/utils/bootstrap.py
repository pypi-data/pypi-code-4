# coding=utf-8
from django.utils.safestring import mark_safe
from html import generate_code


def icon_text(icon, color, text=''):
    if icon == '' or icon is None:
        return ''

    if color == '' or color == 'black':
        color = 'black'
    else:
        color = 'white'

    return generate_code('i', {
        'class': (
            'icon',
            'icon-' + color,
            'icon-' + icon,
        )
    }, text)


def bootstrap_button_dict(text, color, link, icon='', size=''):
    return {
        'text': text,
        'color': color,
        'link': link,
        'icon': icon,
        'size': size
    }


def content(text, icon, color):
    return mark_safe(icon_text(icon, color) + text)


def button_classes(color='', size=''):
    arr = ['btn']
    if color != '' and color is not None:
        arr.append('btn-' + color)

    if size != '' and size is not None:
        arr.append('btn-' + size)
    return arr


def link_button(text, color='', link='#', icon='', size=''):
    return generate_code('a', {
        'class': button_classes(color, size),
        'href': link
    }, content(text, icon, color))


def button(text, color='', button_type='submit', icon='', size='', value=None):
    return generate_code('button', {
        'class': button_classes(color, size),
        'type': button_type,
        'value': value
    }, content(text, icon, color))


def link_button_set(buttons):
    html = generate_code('div', {
        'class': 'btn-group'
    }, start_only=True)
    for button in buttons:
        html += link_button(**button)
    html += '</div>'
    return html