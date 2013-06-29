"""
Serialize data to/from JSON
"""

from django.core.serializers.json import Serializer as JSONSerializer
from django.core.serializers.json import Deserializer as JSONDeserializer

from configfield.dbfields import JSONField


class Serializer(JSONSerializer):
    """
    Convert a queryset to JSON.
    """
    pass


def Deserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of JSON data.
    Takes into account player.base.dbfields.JSONField issues
    """
    for obj in JSONDeserializer(stream_or_string, **options):
        for field in obj.object._meta.local_fields:
            if isinstance(field, JSONField):
                field_name = field.name
                setattr(obj.object, field_name, getattr(obj.object, 'get_%s_json' % field_name)())
        yield obj
