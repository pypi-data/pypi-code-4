from django.conf.urls.defaults import *

urlpatterns = patterns('django_moip.html.redirector.views',
    (r'^pdt/$', 'pdt'),
)
