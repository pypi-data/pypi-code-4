import urlparse
import urllib

from django.template import Library

register = Library()

@register.filter
def strip_page_param(url):
    params = [(k,v) for (k,v) in urlparse.parse_qsl(url) if k != 'page']
    return urllib.urlencode(params)
