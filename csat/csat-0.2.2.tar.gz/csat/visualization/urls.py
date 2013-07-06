from django.conf.urls import patterns, url


urlpatterns = patterns(
    'csat.visualization.views',
    url(r'^view/$', 'standalone_viewer', name='standalone-viewer'),
)
