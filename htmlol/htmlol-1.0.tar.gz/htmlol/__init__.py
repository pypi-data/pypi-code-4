#!/usr/bin/python3
# -*- coding: utf-8

'''
An HTML5-compliant structured HTML construction library
'''

from collections import deque, namedtuple, Iterable
from io import StringIO
import sys

__all__ = ['Document', 'Formatter',
    'escape', 'escape_quote', 'literal', 'print_document', 'render_document']

class Document(object):

    '''
    An HTML5 Document

    Document(*elements)
    '''

    def __init__(self, *body):
        self.body = process_elements(body)

    def __str__(self):
        s = StringIO()
        self.write_to(s)
        return s.getvalue()

    def write_body(self, s):
        [self.write_element(s, e) for e in self.body]

    def write_doctype(self, s):
        s.write('<!DOCTYPE html>')

    def write_element(self, s, e):
        s.write(e.render())
        if not e.void_element:
            for i in e.body:
                self.write_element(s, i)
            s.write(e.render_end())

    def write_to(self, s):
        self.write_doctype(s)
        self.write_body(s)

class Formatter(object):

    '''
    Experimental "pretty" formatter for HTML5 documents.

    NOTE: Not yet guaranteed to emit markup with the same effect as
    print(document). Some significant whitespace may be inserted.
    Intended for debugging purposes.
    '''

    State = namedtuple('FormatterState', ('no_indent',))

    def __init__(self, stream, indent = '  '):
        self.stream = stream
        self.indent = indent
        self.indented = False
        self.newline = False
        self.state = deque()

    def format_document(self, doc):
        doc.write_doctype(self.stream)
        self.write_newline()
        for e in doc.body:
            if self.indent_element(e):
                self.write_newline()
                self.format_element(e)
                self.write_newline()
            else:
                self.format_element(e)
        self.write_newline()

    def format_element(self, e, level = 0):
        self.write(e.render())

        if not e.void_element:
            if e.body:
                indent_body = self.indent_body(e)
                if indent_body:
                    next_level = level + 1
                    self.write_newline()
                    self.write_indent(next_level)
                else:
                    next_level = level

                self.push_state(self.State(not indent_body))

                for i in e.body:
                    if indent_body and (self.newline or self.indent_element(i)):
                        self.write_indent(next_level)
                        self.format_element(i, next_level)
                        self.write_newline()
                    else:
                        self.format_element(i, next_level)

                self.pop_state()

            if indent_body:
                self.write_newline()
                self.write_indent(level)
            self.write(e.render_end())

    def indent_body(self, elem):
        if elem.raw_element or elem.escapable_raw_element or elem.pre_element:
            return False

        return not all(isinstance(e, TextElement) for e in elem.body)

    def indent_element(self, elem):
        return not isinstance(elem, TextElement)

    def push_state(self, s):
        self.state.append(s)

    def pop_state(self):
        self.state.pop()

    def write(self, s):
        self.indented = False
        self.newline = False
        self.stream.write(s)

    def write_indent(self, level):
        if not self.indented and not any(s.no_indent for s in self.state):
            self.write_newline()
            self.indented = True
            self.newline = False
            if level:
                self.stream.write(self.indent * level)

    def write_newline(self):
        if not self.newline and not any(s.no_indent for s in self.state):
            self.indented = False
            self.newline = True
            self.stream.write('\n')

class Element(object):

    '''
    HTML5 {name} Element

    {name}(*elements, **attributes)
    '''

    # Name of element
    element_name = NotImplemented
    # Whether the element is a void element type
    void_element = False
    # Whether the element is a raw element type
    raw_element = False
    # Whether the element is an escapable raw element type
    escapable_raw_element = False
    # Whether contained whitespace is significant to output
    pre_element = False

    def __init__(self, *body, **attrs):
        if self.void_element and body:
            raise ValueError('Body specified for void element {}'
                .format(self.element_name))

        body = process_elements(body, not self.raw_element)

        if (self.raw_element or self.escapable_raw_element) and body_not_text(body):
            raise ValueError('Element body in raw element {}'
                .format(self.element_name))

        self.body = body
        self.attrs = process_attrs(attrs)

    def __str__(self):
        s = StringIO()
        Document(self).write_body(s)
        return s.getvalue()

    def render(self):
        if self.attrs:
            return '<{} {}>'.format(self.element_name, attrs_string(self.attrs))
        return '<{}>'.format(self.element_name)

    def render_end(self):
        return '</{}>'.format(self.element_name)

class TextElement(Element):

    '''
    Plain text HTML5 Element
    '''

    void_element = True

    def __init__(self, text):
        if not isinstance(text, str):
            raise TypeError('TextElement expected str; got {}'
                .format(type(text).__name__))
        super().__init__()
        self.text = text

    def render(self):
        return escape(self.text)

class LiteralElement(TextElement):

    '''
    Unescaped raw markup HTML5 Element
    '''

    def render(self):
        return self.text

def attr_name(name):
    if name.startswith('_'):
        name = name[1:]
    if '_' in name:
        if name.startswith('data_'):
            name = 'data-' + name[5:]
        elif name.startswith('xlink_'):
            name = 'xlink:' + name[6:]
        elif name.startswith('xmlns_'):
            name = 'xmlns:' + name[6:]
        name = name.replace('_', '-')
    return name

def attrs_string(attrs):
    return ' '.join(k if v is True else '{}="{}"'.format(k, escape_quote(v))
        for k, v in attrs if v is not False)

def body_not_text(body):
    return not all(isinstance(i, TextElement) for i in body)

def escape(s, tr = { ord('&'): '&amp;', ord('<'): '&lt;', ord('>'): '&gt;' }):
    '''Escape a str containing markup'''
    return s.translate(tr)

def escape_quote(s, tr = { ord('&'): '&amp;', ord('"'): '&quot;' }):
    '''Escape a str within a double-quoted string'''
    return s.translate(tr)

def literal(t):
    '''Returns an element displaying literal unescaped markup'''
    return LiteralElement(t)

def print_document(doc, file = sys.stdout, formatted = False, newline = True):
    '''
    Prints a document to a stream

    If formatted is True, the experimental formatter will be used.
    If newline is True, a newline will be written after non-formatted document
    '''
    if formatted:
        Formatter(file).format_document(doc)
    else:
        doc.write_to(file)
        if newline:
            file.write('\n')

def process_attrs(attrs):
    return sorted((attr_name(k), v) for k, v in attrs.items()) if attrs else ()

def process_elements(elem, escaped = True):
    def do():
        T = TextElement if escaped else LiteralElement
        for e in elem:
            if isinstance(e, str):
                yield T(e)
            elif isinstance(e, Element):
                yield e
            elif isinstance(e, Iterable):
                for ee in process_elements(e, escaped):
                    yield ee
            else:
                yield T(str(e))
    return tuple(do()) if elem else ()

def render_document(doc, formatted = False, newline = True):
    '''
    Returns a document rendered as a str.

    If formatted is True, the experimental formatter will be used.
    If newline is True, a newline will be written after non-formatted document
    '''
    s = StringIO()
    print_document(doc, s, formatted, newline)
    return s.getvalue()

def create_element_type(name):
    d = { 'element_name': name, '__doc__': Element.__doc__.format(name = name) }

    if name in void:
        d['void_element'] = True
    elif name in raw:
        d['raw_element'] = True
    elif name in escapable_raw:
        d['escapable_raw_element'] = True

    if name == 'pre':
        d['pre_element'] = True

    return type(name, (Element,), d)

# Void elements; cannot contain anything, never have an end tag
void = frozenset(('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'keygen', 'link', 'meta', 'param', 'source', 'track', 'wbr'))
# Raw elements; contain text, but no elements or </name
# Character references will be interpreted literally
raw = frozenset(('script', 'style'))
# Escapable raw elements; contain text but no elements or </name
# Character references will be evaluated
escapable_raw = frozenset(('textarea', 'title'))

# All valid HTML5 elements
element_names = '''
a abbr address area article aside audio b base bdi bdo blockquote body br 
button canvas caption cite code col colgroup data datalist dd del details dfn 
div dl dt em embed fieldset figcaption figure footer form h1 h2 h3 h4 h5 h6 
head header hr html i iframe img input ins kbd keygen label legend li link main 
map mark math menu menuitem meta meter nav noscript object ol optgroup option 
output p param pre progress q rp rt ruby s samp script section select small 
source span strong style sub summary sup table tbody td textarea tfoot th thead 
time title tr track u ul var video wbr
'''

g = globals()

for name in element_names.split():
    g[name] = create_element_type(name)
    __all__.append(name)

# The only element name which coincides with a Python keyword
g['del_'] = g['del']

del g, name
