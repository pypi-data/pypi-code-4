
from django import template
from django.template.loader import get_template

register = template.Library()

class MixinNode(template.Node):
    def __init__(self, template_name, nodelist):
        self.template_name = template_name
        self.nodelist = nodelist

    def render(self, context):
        from django.template.loader_tags import BLOCK_CONTEXT_KEY, BlockNode

        tmpl = get_template(self.template_name)

        block_context = context.render_contex[BLOCK_CONTEXT_KEY]

        for block in tmpl.nodelist.get_nodes_by_type(BlockNode):
            if not block_context.get_node(block.name):
                block_context.push(block.name, block)

        return self.nodelist.render(context)


@register.tag
def mixin(parser, token):
    '''
    Include the blocks from another template, so long as they don't exist in
    this one already.
    '''
    bits = token.split()

    if len(bits) != 2:
        raise template.TemplateSyntaxError(
            "'%' requires exactly one argument." % bits[0]
        )

    template_name = template.Variable(bits[1]).resolve({})
    nodelist = parser.parse()

    return MixinNode(template_name, nodelist)


@register.simple_tag(takes_context=True)
def reuse(context, block_name, **kwargs):
    '''
    Allow reuse of a block within a template.

    {% resuse '_myblock' foo=bar %}
    '''
    from django.template.loader_tags import BLOCK_CONTEXT_KEY
    block = context.render_context[BLOCK_CONTEXT_KEY].get_block(block_name)
    if block is None:
        return ''
    # change to context.push in django 1.7
    context.update(kwargs)
    content = block.render(context)
    context.pop()
    return content
