from django import template
from onesky.inline import *

register = template.Library()


@register.tag(name="trans")
def do_trans2(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, str = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])

    if not (str[0] in ('"', "'") and str[0] == str[-1]):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)

    return TransNode(str[1:-1], 1)


@register.tag(name="trans2")
def do_trans(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, str = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])

    if not (str[0] in ('"', "'") and str[0] == str[-1]):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)

    return TransNode(str[1:-1], 2)


class TransNode(template.Node):
    def __init__(self, str, type):
        self.str = str
        self.type = type

    def render(self, context):
        if self.type == 1:
            return trans(self.str)
        else:
            return trans2(self.str)