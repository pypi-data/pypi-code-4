from tastypie.resources import Resource
from tastypie import fields
from tastypie.cache import SimpleCache
from django.conf import settings

from backends import BACKENDS

from datetime import datetime

class Prediction(object):
    """
        A prediction object representation
    """
    def __init__(self, source=None, points=None):
        self.source = source
        self.points = points

class Point(object):
    time = fields.DateField(attribute='time')
    lat = fields.FloatField(attribute='lat')
    lng = fields.FloatField(attribute='lng')
    altitude = fields.IntegerField(attribute='altitude')
    direction = fields.FloatField(attribute='direction')
    velocity = fields.FloatField(attribute='velocity')

class WindResource(Resource):
    source = fields.CharField(attribute='source')
    points = fields.ListField(attribute='points')
    
    class Meta:
        resource_name = "point-prediction"
        object_class = Prediction
        allowed_methods = ['get']
        cache = SimpleCache(timeout=settings.DJANGO_WINDS_CACHE_TIMEOUT)
        
    def obj_get_list(self, request=None, **kwargs):
        lat = float(kwargs['bundle'].request.GET['lat'])
        lng = float(kwargs['bundle'].request.GET['lng'])
        time = datetime.strptime(kwargs['bundle'].request.GET['time'], "%Y-%m-%d")
        
        source = "ucar_CONUS_5km"
        backend = BACKENDS[source]()

        p = Prediction(
            source=source,
            points=backend.get_wind_at_point(lat, lng, time))
            
        return [p]