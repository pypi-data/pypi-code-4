from django_zen.models import Menu
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django import template


register = template.Library()


class MenuTreeNode(template.Node):
    def __init__(self, template_nodes, menu_id):
        self.template_nodes = template_nodes
        self.menu_id = menu_id

    def _render_node(self, context, node):
        bits = []
        context.push()
        for child in node.get_children().filter(published=True):
            bits.append(self._render_node(context, child))
        context['menu_item'] = node
        context['children'] = mark_safe(''.join(bits))
        rendered = self.template_nodes.render(context)
        context.pop()
        return rendered

    def menu_items(self):
        try:
            root_menu = Menu.objects.get(menu_id=self.menu_id, published=True)
        except Menu.DoesNotExist:
            return []
        if root_menu:
            return root_menu.get_children().filter(published=True)

    def render(self, context):
        roots = self.menu_items()
        bits = [self._render_node(context, node) for node in roots]
        return ''.join(bits)


@register.tag
def menu(parser, token):
    bits = token.contents.split()
    if len(bits) != 2:
        raise template.TemplateSyntaxError(_('%s tag requires a queryset') % bits[0])

    menu_id = template.Variable(bits[1])

    template_nodes = parser.parse(('endmenu',))
    parser.delete_first_token()

    return MenuTreeNode(template_nodes, menu_id)


@register.simple_tag
def active(request, name):
    if request.path == name:
        return ' active '
    return ''
