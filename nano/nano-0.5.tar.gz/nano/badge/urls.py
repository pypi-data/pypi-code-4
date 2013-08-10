from django.conf.urls.defaults import *

from nano.badge.models import *

# from django.contrib import admin
# admin.autodiscover()

badges_dict = {
        'queryset': Badge.objects.all(), #usage_for_model(Language, counts=True),
        'extra_context': { 'me': 'badge' },
        }

urlpatterns = patterns('django.views.generic',
        url(r'^$',                        'list_detail.object_list', badges_dict, 'badge-list'),
        url(r'^(?P<object_id>[0-9]+)/$',  'list_detail.object_detail', badges_dict, 'badge-detail'),
)


