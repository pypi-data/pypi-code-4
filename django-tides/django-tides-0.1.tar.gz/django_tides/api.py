"""
    API Endpoints:
    
    /station_list  # do I need a bounding box?
    /station_tide?station_id&start-time&end-time  # what markup should I use? camel, _, or -
"""

from django.conf.urls import url
from django.contrib.gis.geos import fromstr

from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest
from tastypie import fields

from models import TideStation, WaterLevel

import sys
from decimal import Decimal


class StationResource(ModelResource):
    
    # water_levels = fields.ToManyField(WaterLevelResource,
    #     'waterlevel_set', full=True)
    
    class Meta:
        queryset = TideStation.objects.all()
        resource_name = 'station'
        allowed_methods = ['get']
        excludes = ['id', 'point']
        
        filtering = {
                    "source_id": ('exact',),
                }
                
    def apply_sorting(self, objects, options=None):
        if options and "lat" in options.keys() and "lon" in options.keys():
            point = fromstr("POINT(%s %s)" % (options['lon'], options['lat']))
            return objects.distance(point).order_by('distance')
        return super(StationResource, self).apply_sorting(objects, options)
                
    # def obj_get_list(self, request=None, **kwargs):
    #     
    #     class StationClass:
    #         def __init__(self, name, id, slices):
    #             self.name = name
    #             self.id = id
    #             self.slices = slices
    #     
    #     obj_list = []
    #     for station in self.queryset:
    #         obj = {
    #             'name': station.name,
    #             'lat': station.point.y,
    #             'lon': station.point.x
    #         }
    #         print obj
    #     return object_list
    #         
    #             
    def dehydrate(self, bundle):
        # print >> sys.stderr, "*****BUNDLE*****"
        # print >> sys.stderr, bundle.data['point']
        bundle.data['lat'] = bundle.obj.point.y
        bundle.data['lon'] = bundle.obj.point.x
        return bundle
                
    # children = fields.ToManyField(WaterLevelResource, 'children')
    # 
    # def prepend_urls(self):
    #     return [
    #         url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/children%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_children'), name="api_get_children"),
    #     ]
    # 
    # def get_children(self, request, **kwargs):
    #     try:
    #         obj = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
    #     except ObjectDoesNotExist:
    #         return HttpGone()
    #     except MultipleObjectsReturned:
    #         return HttpMultipleChoices("More than one resource is found at this URI.")
    # 
    #     child_resource = WaterLevelResource()
    #     return child_resource.get_detail(request, parent_id=obj.pk)
    


class WaterLevelResource(ModelResource):
    station = fields.ForeignKey(StationResource, 'station')

    class Meta:
        fields = ['time', 'level', 'station']
        # allowed_methods = None
        queryset = WaterLevel.objects.all().order_by('time')
        resource_name = 'water-level'
        allowed_methods = ['get']
        # 
        filtering = {
            'station': ALL_WITH_RELATIONS,
            'time': ALL,
        }

        # filtering = {
        #     'station__source_id': ['exact',]
        #     'date': ['gte', 'lte'],
        # }

    # def build_filters(self, filters=None):
    #     if ('date__gte' not in filters and
    #         'date__lte' not in filters and
    #         'station__source_id' not in filters:
    #          raise BadRequest # or maybe create your own exception
    #     return super(LinguistResource, self).build_filters(filters)