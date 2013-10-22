import json
import urlparse
import urllib
import requests

from json_pointer import Pointer


class InvalidReferenceError(Exception):
    pass


class Reference(object):
    _registry = {}

    @classmethod
    def register(cls, url, data):
        if url not in cls._registry:
            cls._registry[url] = data

    def __init__(self, ref, base_url=''):
        ref = urlparse.urljoin(base_url, ref)
        self.url, self.fragment = urlparse.urldefrag(ref)

    def get(self):
        try:
            data = self._registry[self.url]
        except KeyError:
            data = json.loads(
                requests.get(
                    self.url,
                    headers={'accept': 'application/json'}
                ).content
            )
            self.register(self.url, data)
        
        pointer = Pointer(urllib.unquote(self.fragment))

        return pointer.get(data)
            
