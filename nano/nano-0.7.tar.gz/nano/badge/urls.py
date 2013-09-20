from django.conf.urls.defaults import *

urlpatterns = patterns('nano.badge.views',
        url(r'^$',                        'list_badges', {}, 'badge-list'),
        url(r'^(?P<object_id>[0-9]+)/$',  'show_badge', {}, 'badge-detail'),
)
