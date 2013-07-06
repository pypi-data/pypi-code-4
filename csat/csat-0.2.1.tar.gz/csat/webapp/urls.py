from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

csat_patterns = patterns(
    'csat.django.apps',
    url(r'^', include(
        'csat.acquisition.urls',
        namespace='acquisiton',
        app_name='acquisition')),
    url(r'^', include(
        'csat.visualization.urls',
        namespace='visualization',
        app_name='visualization')),
)

urlpatterns = patterns(
    '',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(csat_patterns, namespace='csat', app_name='csat')),
)

if settings.DEBUG:
    urlpatterns = patterns(
        '',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'', include('django.contrib.staticfiles.urls')),
    ) + urlpatterns
