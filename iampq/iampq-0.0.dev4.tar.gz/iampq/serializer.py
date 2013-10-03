import codecs
_decode = codecs.decode
import conf

def raw_encode(data):
    content_type = 'application/data'
    payload = data
    if isinstance(payload, unicode):
        content_encoding = 'utf-8'
        payload = payload.encode('utf-8')
    else:
        content_encoding = 'binary'

    return content_type, content_encoding, payload


class SerializerNotInstalled(Exception):
    pass

class SerializerRegistry(object):
    """The registry keeps track of serialization methods"""

    def __init__(self):
        self._encoders = {}
        self._decoders = {}
        self._default_encode = None
        self._default_content_type = None
        self._default_content_encoding = None
        self.type_to_name = {}
        self.name_to_type = {}

    def register(self, name, encoder, decoder, content_type,
            content_encoding='utf-8'):
        if encoder:
            self._encoders[name] = (content_type, content_encoding, encoder)
        if decoder:
            self._decoders[content_type] = decoder
        self.type_to_name[content_type] = name
        self.name_to_type[name] = content_type

    def unregister(self, name):
        try:
            content_type = self.name_to_type[name]
            self._decoders.pop(content_type, None)
            self._encoders.pop(name, None)
            self.type_to_name.pop(content_type, None)
            self.name_to_type.pop(name, None)
        except KeyError:
            raise SerializerNotInstalled(
                'No encoder/decoder installed for %s' % name)

    def _set_default_serializer(self, name):
        try:
            (self._default_content_type, self._default_content_encoding,
                self._default_encode) = self._encoders[name]
        except KeyError:
            raise SerializerNotInstalled(
                'No encoder installed for %s' % name)

    def encode(self, data, serializer=None):
        if serializer == 'raw':
            return raw_encode(data)
        if serializer and not self._encoders.get(serializer):
            raise SerializerNotInstalled(
                'No encoder installed for %s' % serializer)

        if not serializer and isinstance(data, bytes):
            return 'application/data', 'binary', data
        if not serializer and isinstance(data, unicode):
            return 'text/plain', 'utf-8', data
        if serializer:
            content_type, content_encoding, encoder = self._encoders[serializer]
        else:
            encoder = self._default_encode
            content_type = self._default_content_type
            content_encoding = self._default_content_encoding
        payload = encoder(data)
        return content_type, content_encoding, payload

    def decode(self, data, content_type, content_encoding=None,):
        content_type = content_type or 'application/data'
        content_encoding = (content_encoding or 'utf-8').lower()

        if data:
            decode = self._decoders.get(content_type)
            if decode:
                return decode(data)
            return _decode(data, content_encoding)
        return data

registry = SerializerRegistry()


"""
.. function:: encode(data, serializer=default_serializer)

    Serialize a data structure into a string suitable for sending
    as an AMQP message body.

    :param data: The message data to send. Can be a list,
        dictionary or a string.

    :keyword serializer: An optional string representing
        the serialization method you want the data marshalled
        into. (For example, `json`, `raw`, or `pickle`).

        If :const:`None` (default), then json will be used, unless
        `data` is a :class:`str` or :class:`unicode` object. In this
        latter case, no serialization occurs as it would be
        unnecessary.

        Note that if `serializer` is specified, then that
        serialization method will be used even if a :class:`str`
        or :class:`unicode` object is passed in.

    :returns: A three-item tuple containing the content type
        (e.g., `application/json`), content encoding, (e.g.,
        `utf-8`) and a string containing the serialized
        data.

    :raises SerializerNotInstalled: If the serialization method
            requested is not available.
"""
encode = registry.encode

"""
.. function:: decode(data, content_type, content_encoding):

    Deserialize a data stream as serialized using `encode`
    based on `content_type`.

    :param data: The message data to deserialize.

    :param content_type: The content-type of the data.
        (e.g., `application/json`).

    :param content_encoding: The content-encoding of the data.
        (e.g., `utf-8`, `binary`, or `us-ascii`).

    :returns: The unserialized data.

"""
decode = registry.decode

register = registry.register

unregister = registry.unregister

def register_json():
    from simplejson import loads, dumps

    def _loads(obj):
        r"""If object is binary, then decode it to utf-8"""
        if isinstance(obj, bytes):
            obj = obj.decode()
        return loads(obj)

    registry.register(conf.JSON, dumps, _loads,
        content_type=conf.JSON_CONTENT_TYPE,
        content_encoding=conf.JSON_CONTENT_ENCODING)

def register_msgpack():
    try:
        try:
            from msgpack import packb as dumps, unpackb
            loads = lambda s: unpackb(s, encoding='utf-8')
        except ImportError:
            from msgpack import packs as dumps, unpacks as loads
        registry.register(
            conf.MSGPACK, dumps, loads,
            content_type=conf.MSGPACK_CONTENT_TYPE,
            content_encoding=conf.MSGPACK_CONTENT_ENCODING)
    except ImportError:
        pass

register_json()
register_msgpack()