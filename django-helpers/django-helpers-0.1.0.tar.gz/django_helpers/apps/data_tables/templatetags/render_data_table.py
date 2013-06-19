# coding=utf-8
from django.template import TemplateSyntaxError, Node
from django.template.defaulttags import register
from django_helpers.helpers.templatetags import parse_args
from django_helpers.apps.data_tables import get_table

__author__ = 'ajumell'


class DataTableRendererNode(Node):
    def __init__(self, table_name, args=None, kwargs=None):
        self.table_name = table_name
        self.args = args
        self.kwargs = kwargs

    def render(self, context):
        table = get_table(self.table_name)
        return table.safe_string(kwargs=self.kwargs, args=self.args)


@register.tag
def render_data_table(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' needs at least two arguments." % bits[0])
    args, kwargs = parse_args(bits, parser)

    table_name = args[0]
    args = args[1:]
    return DataTableRendererNode(table_name, args, kwargs)