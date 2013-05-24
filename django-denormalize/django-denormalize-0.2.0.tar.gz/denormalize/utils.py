import decimal
import json
import datetime

def to_json(data, indent=2, **kwargs):
    """Serialize data to JSON
    :param data: Data structure to convert to JSON
    :param indent: JSON indenting
    :type indent: int
    :return: JSON string
    :rtype: str
    """
    # See also: http://stackoverflow.com/questions/455580/json-datetime
    return json.dumps(data, indent=indent, default=_json_serializer, **kwargs)


class _fakefloat(float):
    # http://stackoverflow.com/questions/1960516/python-json-serialize-a-decimal
    def __init__(self, value):
        self._value = value
    def __repr__(self):
        return str(self._value)

def _json_serializer(obj):
    """Serialize an object into something that can be represented in JSON"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return _fakefloat(obj)
    else:
        raise TypeError, 'Object of type %s with value of %s is not ' \
                         'JSON serializable' % (type(obj), repr(obj))

