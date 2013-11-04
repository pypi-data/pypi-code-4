from django.conf.urls import handler404, handler500, patterns,\
    url 
from django.http import HttpResponsePermanentRedirect
from . import mh_utils

def redirect(req, path):
    return HttpResponsePermanentRedirect(u'%s/%s' % (mh_utils.get_default_site().site.domain, path,))

urlpatterns = patterns('',
     url(r'^(?P<path>.*)$', redirect),
)
