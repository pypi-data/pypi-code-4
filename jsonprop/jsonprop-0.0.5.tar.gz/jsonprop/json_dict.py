from json_property import json_property
from json_field import json_field
from json_encoder import JsonObjectEncoder
import json

class JsonObject(object):

    def __init__(self, **kwargs):
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])

    def _to_json_dict(self):
        cls = type(self)
        retval = {}
        for key in cls.__dict__:
            item = cls.__dict__[key] 
            if isinstance(item, json_property) or isinstance(item, json_field):
                if item._ser_if_null:
                    retval[item._name] = item.__get__(self)
                elif item.__get__(self):
                    retval[item._name] = item.__get__(self)

        return retval 

    def json(self):
        return json.dumps(self._to_json_dict(), cls=JsonObjectEncoder)

