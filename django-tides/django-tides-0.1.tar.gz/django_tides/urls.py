from django.conf.urls.defaults import *

from api import StationResource, WaterLevelResource

# from views import TideStationList, StationWaterLevel

station_resource = StationResource()
wl_resource = WaterLevelResource()

urlpatterns = patterns('',
    # url(r'^station-list/$', TideStationList.as_view(), name='station-list'),
    # url(r'^water-levels/$', StationWaterLevel.as_view(), name='water-levels'),
    
    (r'^api/', include(station_resource.urls)),
    (r'^api/', include(wl_resource.urls)),
)