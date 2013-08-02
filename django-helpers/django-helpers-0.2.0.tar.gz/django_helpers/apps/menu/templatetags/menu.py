from django.template import Node, TemplateSyntaxError, Library
from .. import get_menu
from django_helpers.helpers.templatetags import parse_args


__author__ = 'ajumell'

register = Library()


class MenuRenderNode(Node):
    def __init__(self, menu_name, args=None, kwargs=None):
        self.menu_name = menu_name
        self.args = args
        self.kwargs = kwargs

    def render(self, context):
        menu_name = self.menu_name.resolve(context)
        menu_cls = get_menu(menu_name)
        menu = menu_cls(context)
        context[menu.menu_id] = menu
        return menu.render()


@register.tag
def render_menu(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' needs at least two arguments." % bits[0])
    args, kwargs = parse_args(bits, parser)

    table_name = args[0]
    args = args[1:]

    return MenuRenderNode(table_name, args, kwargs)