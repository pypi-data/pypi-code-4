from django import template

import houdini as h
import misaka as m
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

register = template.Library()


class MisakaRenderer(m.HtmlRenderer, m.SmartyPants):

    def block_code(self, text, lang):
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % \
                h.escape_html(text.strip())

        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter()

        return highlight(text, lexer, formatter)


@register.filter()
def markdown(value):
    renderer = MisakaRenderer(flags=m.HTML_ESCAPE)
    md = m.Markdown(renderer,
                    extensions=m.EXT_FENCED_CODE | m.EXT_NO_INTRA_EMPHASIS)

    return md.render(value)
