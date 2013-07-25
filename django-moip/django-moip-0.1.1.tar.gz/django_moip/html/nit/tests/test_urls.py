from django.conf.urls.defaults import *

urlpatterns = patterns('django_moip.html.nit.views',
    (r'^ipn/$', 'nit'),
)
