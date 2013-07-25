from django.conf.urls.defaults import *

urlpatterns = patterns('django_moip.html.nit.views',            
    url(r'^$', 'nit', name="moip-nit"),
)