# -*- coding: utf-8 -*-

from __future__ import absolute_import
from markdown import Markdown
import simplejson
from sqlalchemy.types import TypeDecorator, UnicodeText

__all__ = ['RichText']


converters = {
    'markdown': (True, Markdown(safe_mode="escape").convert),
    'html': (False, lambda v: None),
    }


class RenderedUnicode(object):
    def __init__(self, text, html, format):
        self.text = text
        self.html = html
        self.format = format

    def __unicode__(self):
        return self.text

    def __str__(self):
        return self.text.encode('utf-8')

    def __html__(self):
        return self.html

    def __repr__(self):
        return repr(self.text)


class RichText(TypeDecorator):
    """
    Represents a rich text column. Usage::

        column = Column(RichText)
    """
    impl = UnicodeText

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = simplejson.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = simplejson.loads(value, use_decimal=True)
            value = RenderedUnicode(value.get('text'), value.get('html'), value.get('format'))
        return value
