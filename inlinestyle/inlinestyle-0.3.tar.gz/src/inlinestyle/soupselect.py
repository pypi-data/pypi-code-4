"""
soupselect.py

CSS selector support for BeautifulSoup.

soup = BeautifulSoup('<html>...')
select(soup, 'div')
- returns a list of div elements

select(soup, 'div#main ul a')
- returns a list of links inside a ul inside div#main

"""

import re

tag_re = re.compile('^[a-z0-9]+$')

attribselect_re = re.compile(
    r'^(?P<tag>\w+)?\[(?P<attribute>\w+)(?P<operator>[=~\|\^\$\*]?)' + 
    r'=?"?(?P<value>[^\]"]*)"?\]$'
)

# /^(\w+)\[(\w+)([=~\|\^\$\*]?)=?"?([^\]"]*)"?\]$/
#   \---/  \---/\-------------/    \-------/
#     |      |         |               |
#     |      |         |           The value
#     |      |    ~,|,^,$,* or =
#     |   Attribute 
#    Tag

def attribute_checker(operator, attribute, value=''):
    """
    Takes an operator, attribute and optional value; returns a function that
    will return True for elements that match that combination.
    """
    def flatten_attr(el_attr):
        if isinstance(el_attr, list):
            el_attr = ' '.join(el_attr)
        return el_attr

    return {
        '=': lambda el: flatten_attr(el.get(attribute, [''])) == value,
        # attribute includes value as one of a set of space separated tokens
        '~': lambda el: value in el.get(attribute, ['']),
        # attribute starts with value
        '^': lambda el: flatten_attr(el.get(attribute, [''])).startswith(value),
        # attribute ends with value
        '$': lambda el: flatten_attr(el.get(attribute, [''])).endswith(value),
        # attribute contains value
        '*': lambda el: value in flatten_attr(el.get(attribute, [''])),
        # attribute is either exactly value or starts with value-
        '|': lambda el: flatten_attr(el.get(attribute, [''])) == value \
            or flatten_attr(el.get(attribute, [''])).startswith('%s-' % value),
    }.get(operator, lambda el: el.has_key(attribute))


def select(soup, selector):
    """
    soup should be a BeautifulSoup instance; selector is a CSS selector 
    specifying the elements you want to retrieve.
    """
    tokens = selector.split()
    current_context = [soup]
    for index, token in enumerate(tokens):
        if tokens[index - 1] == '>':
            # already found direct descendants in last step
            continue

        m = attribselect_re.match(token)
        if m:
            # Attribute selector
            tag, attribute, operator, value = m.groups()
            if not tag:
                tag = True
            checker = attribute_checker(operator, attribute, value)
            found = []
            for context in current_context:
                found.extend([el for el in context.find_all(tag) if checker(el)])
            current_context = found
            continue

        if '#' in token:
            # ID selector
            tag, id = token.split('#', 1)
            if not tag:
                tag = True
            el = current_context[0].find(tag, {'id': id})
            if not el:
                return [] # No match
            current_context = [el]
            continue

        if '.' in token:
            # Class selector
            tag, klass = token.split('.', 1)
            if not tag:
                tag = True
            classes = set(klass.split('.'))
            found = []

            def is_in_all_classes(class_tag):
                if not isinstance(tag, bool):
                    return class_tag.name == tag \
                            and class_tag.has_key('class') \
                            and classes.issubset(class_tag['class'])
                else:
                    return class_tag.has_key('class') \
                            and classes.issubset(class_tag['class'])

            for context in current_context:
                found.extend(context.find_all(is_in_all_classes))
            current_context = found
            continue

        if token == '*':
            # Star selector
            found = []
            for context in current_context:
                found.extend(context.find_all(True))
            current_context = found
            continue

        if token == '>':
            # Child selector
            tag = tokens[index + 1]
            if not tag:
                tag = True

            found = []
            for context in current_context:
                found.extend(context.findAll(tag, recursive=False))
            current_context = found
            continue

        # Here we should just have a regular tag
        if not tag_re.match(token):
            return []
        found = []
        for context in current_context:
            found.extend(context.find_all(token))
        current_context = found
    return current_context

def monkeypatch(BeautifulSoupClass=None):
    """
    If you don't explicitly state the class to patch, defaults to the most 
    common import location for BeautifulSoup.
    """
    if not BeautifulSoupClass:
        from bs4 import BeautifulSoup as BeautifulSoupClass
    BeautifulSoupClass.findSelect = select

def unmonkeypatch(BeautifulSoupClass=None):
    if not BeautifulSoupClass:
        from bs4 import BeautifulSoup as BeautifulSoupClass
    delattr(BeautifulSoupClass, 'findSelect')
