"""
    API Endpoints:
    
    /station_list  # do I need a bounding box?
    /station_tide?station_id&start-time&end-time  # what markup should I use? camel, _, or -
"""

from django.views.generic import ListView
from django.core import serializers

from models import TideStation, WaterLevel

from django import http
from django.utils import simplejson as json

class JSONResponseMixin(object):
    """
        https://docs.djangoproject.com/en/1.3/topics/class-based-views/#more-than-just-html
    """
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return json.dumps(context)

class TideStationList(JSONResponseMixin, ListView):
    model = TideStation
    
    def get_queryset(self):
        qs = TideStation.objects.all()
        # return serializers.serialize("json", qs)
        return qs
        
    def get_context_data(self, **kwargs):
        return {
            "object_list": serializers.serialize("json", self.get_queryset())
        }

class StationWaterLevel(JSONResponseMixin, ListView):
    """
        /station_tide?station_id&start-time&end-time
    """
    model = WaterLevel
    
    def get_queryset(self):
        key_list = ['station_id', 'start_time', 'end_time']
        if all (k in request.GET.keys() for k in key_list):
            return WaterLevel.objects.filter(
                                                station_id=request.GET['station_id'],
                                                time_lte=self.request.GET['start_time'],
                                                time__gte=self.request.GET['end_time'])