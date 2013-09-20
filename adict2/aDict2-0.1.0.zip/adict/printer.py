# aDict — simple dictionary handling
#
# Authors:
#     arseniiv <arseniiv@gmail.com>
#
# To the extent possible under law, the author(s) have dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication along with this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

"""printer.py — aDict to string/file printer
"""

__all__ = [
    'Printer'
    ]

from adict._data import *
from adict._data import (FORMAT_NONE, FORMAT_SW, FORMAT_EM, FORMAT_REM)
from adict._strings import *


class Printer:
    """Printer of data to aDict-formatted string.
    
    Usage:
    
    p = Printer(dictionary)
    result = str(p)
    """
    
    def __init__(self, data: Dictionary):
        """Create a printer of Dictionary data."""
        self.data = data
    
    def __str__(self):
        v = PrintDictionaryVisitor()
        self.data._accept_visitor(v)
        return str(v)


def _format_none(text):
    return text       

def _format_sw(text):
    return "{1}{0}{1}".format(text, special_word_marker)

def _format_rem(text):
    return "{1}{0}{2}".format(text, *rem_brackets)

def _format_em(text):
    return "{1}{0}{2}".format(text, *em_brackets)

_format_function = {
    FORMAT_NONE: _format_none,
    FORMAT_SW: _format_sw,
    FORMAT_REM: _format_rem,
    FORMAT_EM: _format_em
    }

def formatted(o):
    if isinstance(o, str):
        return o
    elif isinstance(o, list):
        return "".join([_format_function[e[0]](e[1]) for e in o])

def title(e):
    if isinstance(e, tuple):
        word, num = e
    elif isinstance(e, str):
        word = e
        num = 0
    if num == 0:
        return word
    else:
        return "{0} {2} {1}".format(word, num, homonym_separator)


class PrintDictionaryVisitor:
    """Visitor for printing."""
    
    def __init__(self):
        self.lines = []
        self.emit_section(signature_section_name)
        self.has_properties_section = False
        self.has_articles_section = False
        
    def __str__(self):
        return "\n".join(self.lines)
    
    def emit_section(self, name):
        self.lines.append("{1}{0}{2}".format(name, *section_brackets))
    
    def visit_property(self, k, v):
        if (not self.has_properties_section):
            self.emit_section(properties_section_name)
            self.has_properties_section = True
        self.lines.append("{0} {2} {1}".format(k, v, name_value_separator))
    
    def visit_articleStart(self, e):
        if (not self.has_articles_section):
            self.emit_section(articles_section_name)
            self.lines.append("")
            self.has_articles_section = True
    
    def visit_title(self, e):
        self.lines.append(title(e))
    
    def visit_class(self, e):
        self.lines.append("{1}{0}{1}".format(e, special_word_marker))
    
    def visit_form(self, e):
        sw, text = e
        self.lines.append("{2}{0}{2} {1}".format(sw, text, special_word_marker))
    
    def visit_transcription(self, e):
        self.lines.append("{1}{0}{2}".format(e, *transcription_brackets))
    
    def visit_etymology(self, e):
        self.lines.append("{1} {0}".format(formatted(e), etymology_marker))
    
    def visit_link_content(self, e):
        self.lines.append("{1} {0}".format(title(e), link_marker))
    
    def visit_form_content(self, e):
        sw, t = e
        if sw == None:
            self.lines.append("{1} {0}".format(title(t), form_link_marker))
        else:
            self.lines.append("{2} {3}{0}{3} {1}".format(sw, title(t), form_link_marker,
                special_word_marker))
    
    def visit_definition_start(self, e):
        pass
    
    def visit_meaning(self, e):
        self.lines.append("{1} {0}".format(formatted(e), meaning_marker))
    
    def visit_example(self, e):
        t1, t2 = e
        self.lines.append("{1} {0}".format(formatted(t1), example_marker))
        self.lines.append("{1} {0}".format(formatted(t2), translation_marker))
    
    def visit_idiom(self, e):
        t1, t2 = e
        self.lines.append("{1} {0}".format(formatted(t1), idiom_marker))
        self.lines.append("{1} {0}".format(formatted(t2), translation_marker))
    
    def visit_link(self, e):
        f, t = e
        if f == None:
            self.lines.append("{1} {0}".format(title(t), link_marker))
        else:
            self.lines.append("{1}{2} {0}".format(title(t), f, link_marker))
    
    def visit_definition_end(self, e):
        pass
    
    def visit_article_end(self, e):
        self.lines.append("")

