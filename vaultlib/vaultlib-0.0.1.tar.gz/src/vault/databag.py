import rsa
import base64
import json


class Databag(object):

    def __init__(self, _id, data):
        self._id = _id
        self.data = data

    @property
    def id(self):
        return self._id

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def encrypt(self, pk):
        jsonData = self._encode_json(self.data)
        self.data = base64.b64encode(rsa.encrypt(jsonData, pk))

    def decrypt(self, pk):
        jsonData = rsa.decrypt(base64.b64decode(self.data), pk)
        self.data = self._decode_json(jsonData)

    def _encode_json(self, data):
        return json.dumps(data, sort_keys=False, indent=4)

    def _decode_json(self, data):
        return json.loads(data)
