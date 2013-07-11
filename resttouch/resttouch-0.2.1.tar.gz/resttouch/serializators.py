import json

__all__ = ('PlainText', 'SimpleJSON')


class Serializator(object):
    pass


class PlainText(Serializator):
    def deserialzie(self, string):
        return string

    def serialize(self, obj):
        return obj
        

class SimpleJSON(Serializator):
    def deserialize(self, string):
        return json.loads(string)

    def serialize(self, obj):
        return json.dumps(obj)