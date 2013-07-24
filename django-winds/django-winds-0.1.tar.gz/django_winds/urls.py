from django.conf.urls.defaults import *

from api import WindResource
wind_resource = WindResource()

urlpatterns = patterns('',
    (r'^api/', include(wind_resource.urls)),
)