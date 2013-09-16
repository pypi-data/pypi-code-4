import json
import urllib2
import uuid
from webapi.protojson import encode_message
import logging
import sys

VERSION = '2.0'

class JsonRpcClient(object):

    def __init__(self, uri, headers=None):
        self.uri = uri
        self.headers = headers or {}

    def call(self, method, params, upload=None):
        # TODO: support upload

        parameters = {
            'id': str(uuid.uuid4()),
            'method': method,
            'params': params,
            'jsonrpc': VERSION
        }
        data = encode_message(parameters)

        headers = {
            "Content-Type": "application/json"
        }
        headers = dict(headers.items() + self.headers.items())
        req = urllib2.Request(self.uri, data, headers)

        logging.debug('Sending %s', data)
        print >> sys.stderr, "SENDING", data
        response = urllib2.urlopen(req).read()

        try:
            result = json.loads(response)
        except:
            return None

        logging.debug('Got response %s', result)

        if 'error' in result:
            raise Exception('%s Code: %s' % (result['error']['message'], result['error']['code']))


        if parameters['id'] == result['id'] and 'result' in result:
            return result['result']
        else:
            return None


class Client(JsonRpcClient):
    def call(self, method, message=None, upload=None):
        # encode the message param
        if message is not None:
            params = [message]
        else:
            params = []

        super(Client, self).call(method, params, upload)
