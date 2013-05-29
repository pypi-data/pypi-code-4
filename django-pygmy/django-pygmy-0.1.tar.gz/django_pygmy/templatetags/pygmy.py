from classytags.core import Tag, Options
from classytags.arguments import Argument, MultiKeywordArgument
from django import template
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

register = template.Library()


class Pygmy(Tag):
    name = 'pygmy'
    options = Options(
        Argument('code'),
        MultiKeywordArgument('kwargs', required=False),
    )

    def render_tag(self, context, code, kwargs):
        # TODO: allow to use custom lexer
        lexer = get_lexer_by_name('python', stripall=True)
        # TODO: ensure correct kwargs before passing to pygments
        # TODO: generic formatter for line numbers with anchors
        formatter = HtmlFormatter(**kwargs)
        output = highlight(code, lexer, formatter)
        return output

register.tag(Pygmy)
