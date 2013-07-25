from django.conf.urls.defaults import *

urlpatterns = patterns('django_moip.html.redirector.views',
    url(r'^$', 'redirector', name="moip-redirector"),
)