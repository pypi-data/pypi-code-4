import pprint as pprint_mod
from django.template import defaultfilters, Library
from django.utils import simplejson as json


register = Library()


@register.filter
def json_format(value):
    """
    Returns a pretty formatted json format
    """
    return json.dumps(value, indent=2)


@register.filter
def pprint(value, width=40):
    """
    Returns a pretty formatted python object
    """
    return pprint_mod.pformat(value, width=width)


@register.inclusion_tag('base/inc.head.html')
def head(heading, head_id=None, head_type='h3'):
    head_id = head_id or defaultfilters.slugify(heading)
    return {'heading': heading, 'head_id': head_id, 'head_type': head_type}
