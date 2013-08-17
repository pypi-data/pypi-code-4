from json_property import json_property
import json

class JsonObject(object):
    def _to_json_dict(self):
        cls = type(self)
        retval = {}
        for key in cls.__dict__:
            item = cls.__dict__[key] 
            if isinstance(item, json_property):
                if item._ser_if_null:
                    retval[item.prefix] = item.__get__(self)
                elif item.__get__(self):
                    retval[item.prefix] = item.__get__(self)

        return retval 

    def json(self):
        return json.dumps(self._to_json_dict())


