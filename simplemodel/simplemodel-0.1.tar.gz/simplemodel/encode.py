import json

from .model import SimpleModel

class SimpleModelEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SimpleModel):
            return dict(obj)
        return super(SimpleModelEncoder, self).default(obj)
