from django import template, get_version
from django.template import TemplateSyntaxError
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer


if get_version()[:3] == '1.3':
    from django.template.defaulttags import token_kwargs
else:
    from django.template.base import token_kwargs

try:
    unicode
except NameError:
    # Python 3
    basestring = unicode = str

register = template.Library()


def colorize(code, *args, **kwargs):
    # code is empty or it is not a string
    if not (code.strip() and isinstance(code, basestring)):
        error_msg = 'Could not found any valid code to parse.'
        raise TemplateSyntaxError(error_msg)

    # TODO: allow to use custom lexer class
    lexer = kwargs.pop('lexer', None)
    if not lexer:
        lexer = guess_lexer(code).aliases[0]
    lexer = get_lexer_by_name(lexer.lower(), stripall=True)

    # TODO: ensure correct kwargs before passing to pygments
    # TODO: generic formatter for line numbers with anchors
    formatter = HtmlFormatter(**kwargs)
    output = highlight(code, lexer, formatter)
    return output


class PygmyNode(template.Node):
    def __init__(self, code, options):
        self.code = code
        self.options = options

    def render(self, context):
        values = dict([(name, var.resolve(context)) for name, var
                       in self.options.items()])
        context.update(values)
        code = template.Variable(self.code).resolve(context)
        output = colorize(code, **values)
        context.pop()
        return output


@register.tag
def pygmy(parser, token):
    bits = token.split_contents()

    if len(bits) < 2:
        raise TemplateSyntaxError("%r tag takes at least one argument." % bits[0])

    if len(bits) >= 2 and bits[-2] == 'as':
        bits = bits[-1]

    options = token_kwargs(bits[2:], parser, support_legacy=False)
    return PygmyNode(bits[1], options)
