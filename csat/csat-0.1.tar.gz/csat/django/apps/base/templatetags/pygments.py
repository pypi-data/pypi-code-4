from __future__ import absolute_import
from coffin import template
from jinja2 import Markup

from pygments import highlight
from pygments.lexers import get_lexer_for_mimetype, guess_lexer
from pygments.formatters import HtmlFormatter


register = template.Library()


def pygment(content, mime=None):
    if mime:
        lexer = get_lexer_for_mimetype(mime, stripall=True)
    else:
        lexer = guess_lexer(content)
    formatter = HtmlFormatter(linenos='table')
    code = highlight(content, lexer, formatter)
    return Markup(code)

register.filter('pygment', pygment)
