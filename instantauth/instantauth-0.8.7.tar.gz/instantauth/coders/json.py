
from __future__ import absolute_import

import json
import collections
from . import BaseCoder

OrderedJsonDecoder = json.JSONDecoder(object_pairs_hook=collections.OrderedDict)

class JsonCoder(BaseCoder):
    def encode(self, data):
        return json.dumps(data, separators=(',',':')) # compact form

    def decode(self, data):
        return OrderedJsonDecoder.decode(data)