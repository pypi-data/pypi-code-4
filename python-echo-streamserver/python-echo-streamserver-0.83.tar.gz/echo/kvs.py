""" Key-Value Store API

The store is a simple Key-Value database created to store the third-party widgets' arbitrary data elements permanently. Keys are arbitrary strings. Values are never interpreted by Echo. Each data element has public flag indicating if it is readable only by the owner or by everyone.

Each application key has its own independent store.
"""
from echo.core_api import EchoClient, StreamServerError

try:
    import cPickle as pickle
except ImportError:
    import pickle

# TODO: Allow other serializers, e.g. JSON encoding.

def serialize(value):
    return pickle.dumps(value)

def deserialize(value):
    return pickle.loads(value)

# Define the exception on a de-serializing error.
DeserializingError = pickle.UnpicklingError

# ======================================================================

class Client(EchoClient):
    def put(self, key, value, public=True):
        """ Save a data element to the store. The public flag indicates that it is readable by everyone. """
        param_d = {
            'key': key,
            'value': serialize(value), # serialize objects, e.g. pickle.
            'public': public,
        }
        r = self._send_request('kvs/put', param_d, http_post=True)
        # Return True on success.
        if 'result' in r and r['result'] == 'success':
            return True
        else:
            return False

    def _edit(self, key, api_method='kvs/get', raise_not_found=False):
        """ Edit (get or delete) a data element by the key. """
        param_d = {
            'key': key,
            'appkey': self._account._appkey,
        }
        # Set r to dummy JSON value.
        r = {}
        try:
            r = self._send_request(api_method, param_d, http_post=False)
        except StreamServerError, e:
            # Trap 'not_found', but re-raise everything else.
            if (not raise_not_found) and (e.errorCode == 'not_found'):
               pass
            else:
               raise
        # Return value, when present (may be serialized or pickled).
        if 'value' in r:
            try:
                # De-serialize objects, e.g. unpickle.
                return deserialize(str(r['value']))
            except DeserializingError:
                # Return a string when the value is not really pickled.
                return r['value']
        elif 'result' in r:
            return r['result']
        else:
            return None

    def get(self, key, raise_not_found=False):
        """ Fetch a data element by the key. """
        return self._edit(key, api_method='kvs/get', raise_not_found=raise_not_found)

    def delete(self, key, raise_not_found=False):
        """ Delete a data element by the key. """
        return self._edit(key, api_method='kvs/delete', raise_not_found=raise_not_found)

# Module-level client exposes API
# ======================================================================

def put(key, value, public=True):
    """ Save a data element to the store. The public flag indicates that it is readable by everyone. """
    return Client.get_client().put(key, value, public=public)

def get(key, raise_not_found=False):
    """ Fetch a data element by the key. """
    return Client.get_client().get(key, raise_not_found=raise_not_found)

def delete(key, raise_not_found=False):
    """ Delete a data element by the key. """
    return Client.get_client().delete(key, raise_not_found=raise_not_found)

