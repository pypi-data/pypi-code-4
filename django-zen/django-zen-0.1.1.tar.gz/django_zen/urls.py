from django.conf.urls import patterns, url, include
from django_zen.views import page


urlpatterns = patterns('',
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^(?P<url>.*)$', page),
)
