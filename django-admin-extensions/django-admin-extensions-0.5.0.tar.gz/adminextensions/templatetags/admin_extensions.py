from django import template

register = template.Library()


@register.tag
def object_tool(parser, token):
    return ObjectToolNode.handle(parser, token)


class ObjectToolNode(template.Node):

    @classmethod
    def handle(cls, parser, token):
        bits = token.split_contents()
        tool = parser.compile_filter(bits[1])
        as_var = None
        link_class = None

        if len(bits) > 2 and bits[-2] == 'as':
            as_var = bits[-1]
            bits = bits[:-2]

        if len(bits) > 2:
            link_class = parser.compile_filter(bits[2])

        return cls(tool, link_class=link_class, as_var=as_var)

    def __init__(self, tool, link_class=None, as_var=None):
        self.tool = tool
        self.link_class = link_class
        self.as_var = as_var

    def render(self, context):
        tool = self.tool.resolve(context)
        kwargs = {}

        if self.link_class:
            kwargs['link_class'] = self.link_class.resolve(context)

        out = tool(context, **kwargs)

        if self.as_var:
            context[self.as_var] = out
            return ''

        return out
