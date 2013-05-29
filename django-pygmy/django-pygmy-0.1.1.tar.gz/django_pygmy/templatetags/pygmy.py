from classytags.core import Tag, Options
from classytags.arguments import Argument, MultiKeywordArgument
from django import template
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer

register = template.Library()


class Pygmy(Tag):
    name = 'pygmy'
    options = Options(
        Argument('code'),
        MultiKeywordArgument('kwargs', required=False),
    )

    def render_tag(self, context, code, kwargs):
        # TODO: allow to use custom lexer class
        lexer = kwargs.pop('lexer', None)
        if not lexer:
            lexer = guess_lexer(code).name
        lexer = get_lexer_by_name(lexer.lower(), stripall=True)

        # TODO: ensure correct kwargs before passing to pygments
        # TODO: generic formatter for line numbers with anchors
        formatter = HtmlFormatter(**kwargs)
        output = highlight(code, lexer, formatter)
        return output

register.tag(Pygmy)
