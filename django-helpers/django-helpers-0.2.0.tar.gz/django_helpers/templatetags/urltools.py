from urlparse import urlparse, urlunparse

from django.http import QueryDict
from django import template
from django.template import TemplateSyntaxError
from django_helpers.helpers.templatetags import parse_args, TemplateNode


register = template.Library()

# Copied from https://github.com/fatbox/fatbox-django-utils/blob/master/fatbox_utils/templatetags/urltools.py


@register.simple_tag(takes_context=True)
def abs_uri(context, relative_url):
    if 'request' not in context:
        return relative_url
    return context['request'].build_absolute_uri(relative_url)


@register.simple_tag(takes_context=True)
def modify_qs(context, **kwargs):
    if 'request' not in context:
        return 'You need to enable the request context processor!'

    # thanks to: http://stackoverflow.com/a/12423248
    # updated to allow None to delete an element
    url = context['request'].get_full_path()
    (scheme, netloc, path, params, query, fragment) = urlparse(url)
    query_dict = QueryDict(query).copy()
    for key in kwargs:
        query_dict_key = key
        if key in context:
            query_dict_key = context[key]

        if kwargs[key] is None:
            if query_dict_key in query_dict:
                del query_dict[query_dict_key]
        else:
            query_dict[query_dict_key] = kwargs[key]
    query = query_dict.urlencode()
    return urlunparse((scheme, netloc, path, params, query, fragment))


# class URLNode(TemplateNode):
#     def render(self, context):
#         if 'request' not in context:
#             return 'You need to enable the request context processor!'
#         url = context['request'].get_full_path()
#         print self.kwarg, self.args
#         return url
#
#
# @register.tag
# def modify_qs(parser, token):
#     bits = token.split_contents()
#     print bits
#     if len(bits) < 2:
#         raise TemplateSyntaxError("'%s' needs at least two arguments." % bits[0])
#     args, kwargs = parse_args(bits, parser)
#     return URLNode(args, kwargs)