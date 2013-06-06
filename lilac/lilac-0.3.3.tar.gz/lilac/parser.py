# coding=utf8

"""this module provides a parser to parse post's source to post instance"""


from . import charset
from .models import Post
from .exceptions import *

from datetime import datetime

import toml
import misaka
import houdini
from misaka import HtmlRenderer, SmartyPants
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound


class ColorRender(HtmlRenderer, SmartyPants):
    """misaka render with color codes feature"""

    def _code_no_lexer(self, text):
        # encode to utf8 string
        text = text.encode(charset).strip()
        return(
            """
            <div class="highlight">
              <pre><code>%s</code></pre>
            </div>
            """ % houdini.escape_html(text)
        )

    def block_code(self, text, lang):
        """text: unicode text to render"""

        if not lang:
            return self._code_no_lexer(text)

        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except ClassNotFound:  # lexer not found, use plain text
            return self._code_no_lexer(text)

        formatter = HtmlFormatter()

        return highlight(text, lexer, formatter)


class Parser(object):
    """This initialize an instance so called parser to parse posts from source
    to post instance
    Usage::

        parser = Parser()
        parser.parse(str)   # return post instance
        parser.parse_from(str)  # parse from file's path
        parser.markdown.render(markdown_str)  # render markdown to html
    """

    separator = '---'  # separator between toml header and markdown body

    def __init__(self):
        """Initialize the parser, set markdown render handler as
        an attribute `markdown` of the parser"""
        render = ColorRender()  # initialize the color render
        extensions = (
            misaka.EXT_FENCED_CODE |
            misaka.EXT_NO_INTRA_EMPHASIS |
            misaka.EXT_AUTOLINK
        )

        self.markdown = misaka.Markdown(render, extensions=extensions)

    def parse(self, source):
        """Parse unicode post source to <Post object>"""
        lines = source.splitlines()

        l = None  # flag: if there is separator

        for line_no, line in enumerate(lines):
            if self.separator in line:
                l = line_no  # got the separator's line number
                break

        if not l:
            raise SeparatorNotFound

        # seperate header and body from source
        header, body = "\n".join(lines[:l]), "\n".join(lines[l+1:])

        # check header's validation

        try:
            attrs = toml.loads(header)
        except toml.TomlSyntaxError:  # if header syntax error
            raise PostHeaderSyntaxError

        #TODO: Check title and datetime's type

        if 'title' not in attrs:
            raise PostTitleNotFound

        if 'datetime' not in attrs:
            raise PostDateTimeNotFound
        else:
            try:
                attrs['datetime'] = datetime.strptime(
                    attrs["datetime"], "%Y-%m-%d %H:%M")
            except ValueError:
                raise PostDateTimeInvalid

        tags = attrs.get('tags', [])  # tags is optional

        if not isinstance(tags, list):
            raise PostTagsTypeInvalid

        attrs['markdown'] = body  # append markdown to attributes
        return Post(**attrs)

    def parse_from(self, filepath):
        """parse from filepath, return <Post object>"""
        return self.parse(open(filepath).read().decode(charset))


parser = Parser()  # build a runtime parser
