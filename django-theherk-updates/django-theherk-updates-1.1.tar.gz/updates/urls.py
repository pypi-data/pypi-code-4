from django.conf.urls.defaults import *

urlpatterns = patterns(
    'updates.views',
    url(r'^$', 'index', name='index'),
)
