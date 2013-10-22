import json
import urlparse
import urllib
import requests

from json_pointer import Pointer


class InvalidReferenceError(Exception):
    pass


class Reference(object):
    """
    JSON reference makes it possible to retrieve (parts of) json-objects. See
    http://tools.ietf.org/html/draft-pbryan-zyp-json-ref-00

    >>> import json_reference
    >>> json_reference.Reference('http://json-schema.org/draft-04/schema#/definitions').get()
    
    It is also possible to register references for offline access
    
    >>> json_reference.register('http://localhost/test', {'test': 'bli'})
    
    >>> json_reference.Reference('http://localhost/test').get()
    {'test': 'bli'}

    """
    _registry = {}

    @classmethod
    def register(cls, url, data):
        """ Register reference for offline access
        """
        if url not in cls._registry:
            cls._registry[url] = data

    def __init__(self, ref, base_url=''):
        ref = urlparse.urljoin(base_url, ref)
        self.url, self.fragment = urlparse.urldefrag(ref)

    def _retrieve(self):
        response = requests.get(
            self.url,
            headers={'accept': 'application/json'}
        )
        
        if response.status_code != 200:
            raise InvalidReferenceError(
                "Error retrieving reference: %s" % response.content
            )

        try:
            return json.loads(response.content)
        except ValueError, e:
            raise InvalidReferenceError(
                "Error parsing JSON: %s" % e
            )

    def get(self):
        """
        Retrieve the contents of the reference
        """
        try:
            data = self._registry[self.url]
        except KeyError:
            data = self._retrieve()
        
        pointer = Pointer(urllib.unquote(self.fragment))

        return pointer.get(data)
            
