### -*- coding: utf-8 -*- ####################################################

from django.conf.urls.defaults import *

urlpatterns = patterns('rating.views',

    url(r'rate/(?P<score>\w+)/(?P<content_type_id>\d+)/(?P<field_name>\w+)/(?P<object_id>\d+)/$', 
        'rating_view', name="rate"),
    
)
