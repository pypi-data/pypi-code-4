# -*- coding: utf-8 -*-
from django.template import Library

register = Library()


class Pic:
    image = ''
    thumb = ''
    alt = ''
    width = None
    height = None
    margin = ''

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)


@register.inclusion_tag('pwutils/lightbox.html')
def lightbox(image, thumb, alt='', width=None, height=None, margin='', style=None):

    context = {}
    context['picture'] = Pic(
        image=image,
        thumb=thumb,
        alt=alt,
        width=width,
        height=height,
        margin=margin,
        style=style,
    )
    return context
