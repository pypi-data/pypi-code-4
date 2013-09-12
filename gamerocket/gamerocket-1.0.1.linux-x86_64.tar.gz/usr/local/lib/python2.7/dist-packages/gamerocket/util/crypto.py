from urllib import urlencode, quote
import base64
import hashlib

class Crypto(object):
    
    def __init__(self, config):
        self.config = config
        self.environment = self.config.environment
    
    def sign(self, method, url, parameters, secretKey):        
        base_string = self._build_base_string(method, url, parameters)
        return self._sign(base_string, secretKey)
    
    def _build_base_string(self, method, url, parameters):
        parameters = self.config.sort_dict(parameters)
        base_string = method + "&" + quote(url.lower(), '') + "&"
        
        qs = ''
        if parameters != {}:
            qs = urlencode(parameters)
        
        base_string = base_string + quote(qs)
        return base_string
    
    def _sign(self, base_string, secretKey):
        to_sha256 = hashlib.sha256()
        to_sha256.update(base_string + secretKey)
        string_sha256 = to_sha256.hexdigest()
        string_base64 = base64.b64encode(string_sha256)
        return string_base64