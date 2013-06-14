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

        if len(bits) > 2:
            return cls(tool, parser.compile_filter(bits[2]))

        return cls(tool)

    def __init__(self, tool, link_class=None):
        self.tool = tool
        self.link_class = link_class

    def render(self, context):
        tool = self.tool.resolve(context)
        kwargs = {}

        if self.link_class:
            kwargs['link_class'] = self.link_class.resolve(context)

        return tool(context, **kwargs)
