"""Improved JSON encoder and 'dumps' function."""

import datetime
import json


class ImprovedJSONEncoder(json.JSONEncoder):

    """Improved JSON encoder that can encode special Python types."""

    def default(self, obj):
        """Try to serialize unserializable object and return the result.

        * if object is of type :py:class:`datetime.datetime`, format it to
          ``%Y-%m-%dT%H:%M:%S.%f%z`` string.
        * if object is :py:class:`set` or :py:class:`frozenset`, convert it
          to list
        * otherwise return object string representation (:py:func:`repr`).

        :param obj: object to encode.

        """
        if isinstance(obj, datetime.datetime):
            obj = obj.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        elif isinstance(obj, (set, frozenset)):
            obj = list(obj)
        else:
            obj = repr(obj)
        return obj


def dumps(value, **kwargs):
    """Return value dumped to JSON string using :class:`ImprovedJSONEncoder`.

    :param value: value to be dumped.

    """
    return json.dumps(value, cls=ImprovedJSONEncoder, **kwargs)
