try:
    import simplejson as json
except ImportError:
    import json


def encode_object(obj):
    if hasattr(obj, '__getstate__'):
        return obj.__getstate__
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return obj


def dumps(obj, skipkeys=True, default=encode_object, **kwargs):
    return json.dumps(obj, skipkeys=skipkeys, default=default, **kwargs)


def loads(s, **kwargs):
    return json.loads(s, **kwargs)


def dump(obj, stream, skipkeys=True, default=encode_object, **kwargs):
    return json.dump(obj, stream, skipkeys=skipkeys, default=default, **kwargs)


def load(file_obj, **kwargs):
    return json.load(file_obj, **kwargs)
