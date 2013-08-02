__author__ = 'ajumell'

from json import dumps
from hashlib import md5

from django.http import HttpResponse
from django.conf.urls import url

from autocomplete import AutoComplete
import urls

_REGISTRY = dict()
url_prefix = 'auto-complete-'


def autocomplete_lookup(request, lookup, **kwargs):
    """

    @param request: django.http.HttpRequest
    @param lookup: name of the lookup
    @param kwargs: extra url parameters
    @return: django.http.HttpResponse
    """
    # If lookup does not exists then return blank array.
    # This is prevent any exceptions at runtime.
    if lookup not in _REGISTRY:
        return HttpResponse("[]")

    auto_complete = _REGISTRY[lookup]()

    results = auto_complete.get_results(request, kwargs)
    return HttpResponse(dumps(results))


def create_reg(name):
    return "(?P<%s>.*)/" % name


def register(autocomplete_class):
    if isinstance(autocomplete_class, AutoComplete):
        raise Exception("AutoComplete class is required not instance.")

    if not hasattr(autocomplete_class, 'name'):
        name = md5(unicode(autocomplete_class)).hexdigest()
    else:
        name = getattr(autocomplete_class, 'name')

    if not name.startswith(url_prefix):
        name = url_prefix + name

    setattr(autocomplete_class, 'name', name)

    if name in _REGISTRY:
        return

    _REGISTRY[name] = autocomplete_class
    reg = "%s/" % name
    extra_url_parameters = autocomplete_class.url_search_parameters
    if extra_url_parameters is not None:
        for parameter in extra_url_parameters:
            reg += create_reg(parameter)
    reg += "$"

    pattern = url(r"%s" % reg, autocomplete_lookup, name=name, kwargs={
        "lookup": name
    })
    urls.urlpatterns.append(pattern)
    return autocomplete_class