from __future__ import absolute_import
import json
from protorpc.protojson import ProtoJson, MessageJSONEncoder

class Encoder(ProtoJson):
    def encode_message(self, message):
        # override encode message ignoring check_initialized
        return json.dumps(message, cls=MessageJSONEncoder, protojson_protocol=self)
    
    def decode_dictionary(self, message_type, dictionary):
        assert isinstance(dictionary, dict)
        message = getattr(ProtoJson, '_ProtoJson__decode_dictionary')(self, message_type, dictionary)
        message.check_initialized()
        return message 


def encode_message(message):
    return Encoder().encode_message(message)

def decode_dictionary(message, dictionary):
    return Encoder().decode_dictionary(message, dictionary)