"""
Template tags
"""

import caddstat

from django.template import Library

register = Library()


@register.simple_tag()
def caddstatversion():
    """
    The current version
    """

    return caddstat.__version__
