"""The default delivery mode used for messages. The value is an integer,
    or alias string.

        * 1 or `"transient"`

            The message is transient. Which means it is stored in
            memory only, and is lost if the server dies or restarts.

        * 2 or "persistent" (*default*)
            The message is persistent. Which means the message is
            stored both in-memory, and on disk, and therefore
            preserved if the server dies or restarts."""

TRANSIENT_DELIVERY_MODE = 1

PERSISTENT_DELIVERY_MODE = 2

SERIALIZERS = MSGPACK, JSON = ('msgpack', 'json')
MSGPACK_CONTENT_TYPE, MSGPACK_CONTENT_ENCODING = 'application/x-msgpack', 'binary'
JSON_CONTENT_TYPE, JSON_CONTENT_ENCODING = 'application/json', 'utf-8'