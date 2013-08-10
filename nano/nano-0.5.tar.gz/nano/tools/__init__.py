import logging
import unicodedata
from itertools import izip_longest

_LOG = logging.getLogger(__name__)

from django.conf import settings
from django.contrib.auth.models import SiteProfileNotAvailable
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render_to_response
from django.template import RequestContext, loader, Context
from django.db.models import get_model

def nullfunction(return_this=None, *args, **kwargs):
    "Do-nothing dummy-function"
    return return_this

def pop_error(request):
    error = request.session.get('error', None)
    if 'error' in request.session:
        del request.session['error']
    return error

def asciify(string):
    string = unicodedata.normalize('NFKD', string)
    return string.encode('ascii', 'ignore')

def render_page(request, *args, **kwargs):
    return render_to_response(context_instance=RequestContext(request), *args, **kwargs)

def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

def get_profile_model():
    if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
        error = "AUTH_PROFILE_MODULE isn't set in the settings, couldn't fetch profile"
        _LOG.error(error)
        raise SiteProfileNotAvailable, error
    try:
        app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
        model = get_model(app_label, model_name)
    except ImportError:
        error = "Could not import the profile '%s' given in AUTH_PROFILE_MODULE" % settings.AUTH_PROFILE_MODULE
        _LOG.error(error)
        raise SiteProfileNotAvailable, error
    except ImproperlyConfigured:
        error = "An unknown error happened while fetching the profile model"
        raise SiteProfileNotAvailable, error
    return model

def get_user_model():
    app_label, model_name = getattr(settings, 'NANO_USER_MODEL', 'auth.User').split('.')
    return get_model(app_label, model_name)

if 'nano.blog' in settings.INSTALLED_APPS:
    try:
        from nano.blog import add_entry_to_blog
    except ImportError:
        add_entry_to_blog = nullfunction
else:
    add_entry_to_blog = None
