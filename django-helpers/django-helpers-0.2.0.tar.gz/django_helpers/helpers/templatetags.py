# coding=utf-8
from django import template
from django.template.base import kwarg_re, TemplateSyntaxError, Node

__author__ = 'ajumell'


class TemplateNode(Node):
    def __init__(self, args=None, kwargs=None):
        self.args = args
        self.kwarg = kwargs


def parse_args(bits, parser):
    """

    @param bits: The token bits.
    @param parser: The template parser give to tag.
    @return: arguments and keyword arguments.
    """
    args = []
    kwargs = {}
    for bit in bits[1:]:
        match = kwarg_re.match(bit)
        if not match:
            raise TemplateSyntaxError("Malformed arguments to %s tag" % bits[0])
        name, value = match.groups()
        val = parser.compile_filter(value)
        if name:
            kwargs[name] = val
        else:
            if len(kwargs) == 0:
                args.append(val)
            else:
                raise TemplateSyntaxError("A normal argument cannot preceed keyword argument.")
    return args, kwargs


def resolve_args(args, kwargs, context):
    new_args = []
    new_kwargs = {}

    if args is not None:
        for arg in args:
            new_args.append(arg.resolve(context))

    if kwargs is not None:
        for kwarg in kwargs:
            new_kwargs[kwarg] = kwargs[kwarg].resolve(context)

    if kwargs is not None and args is not None:
        return new_args, new_kwargs

    if kwargs is not None:
        return new_kwargs

    if args is not None:
        return new_args


def create_context_from_kwargs(kwargs, new_context, names, context):
    for name in names:
        if kwargs.has_key(name):
            new_context[name] = kwargs[name].resolve(context)


def parse_verbatim(parser, endtag):
    text = []
    while 1:
        token = parser.tokens.pop(0)
        if token.contents == endtag:
            break
        if token.token_type == template.TOKEN_VAR:
            text.append('{{ ')
        elif token.token_type == template.TOKEN_BLOCK:
            text.append('{% ')
        text.append(token.contents)
        if token.token_type == template.TOKEN_VAR:
            text.append(' }}')
        elif token.token_type == template.TOKEN_BLOCK:
            text.append(' %}')
    return ''.join(text)