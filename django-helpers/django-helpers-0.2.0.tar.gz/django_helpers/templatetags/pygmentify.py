# encoding: utf-8

"""
A filter to highlight code blocks in html with Pygments and BeautifulSoup.

    {% load highlight_code %}

    {{ var_with_code|highlight|safe }}
"""

import pygments
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name, get_all_lexers

from django import template
from django.template import Context

from django.template.defaultfilters import stringfilter
from django_helpers.helpers.templatetags import parse_verbatim

register = template.Library()


def _highlight_html(code, lexer='html+django'):
    try:
        code = code.lstrip('\n')
        code = code.rstrip()
        lexer = get_lexer_by_name(lexer)
        formatter = HtmlFormatter(cssclass='codehilite', linenos='inline')
        code_hl = pygments.highlight(code, lexer, formatter)
        return code_hl
    except:
        raise


@register.filter
@stringfilter
def highlight_var(html):
    return _highlight_html(html)


@register.simple_tag(takes_context=False)
def highlight_file(name, *args):
    fp = file(name)
    html = fp.read()
    fp.close()
    return _highlight_html(html)


class HighlightBlock(template.Node):
    def __init__(self, contents, code_format):
        self.contents = contents
        self.format = code_format

    def render(self, context):
        return _highlight_html(self.contents, self.format)

# noinspection PyUnusedLocal
@register.tag
def highlight(parser, token):
    bits = token.contents.split()
    code_format = bits[1] if len(bits) > 1 else 'html+django'
    contents = parse_verbatim(parser, 'endhighlight')
    return HighlightBlock(contents, code_format)