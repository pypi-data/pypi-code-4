import sys
import os
from collections import OrderedDict
import gamerocket
import gamerocket.util.http_strategy.pycurl_strategy

class Configuration(object):
    
    @staticmethod
    def configure(environment, apiKey, secretKey):
        Configuration.environment = environment
        Configuration.apiKey = apiKey
        Configuration.secretKey = secretKey
        Configuration.use_unsafe_ssl = False
    
    @staticmethod
    def gateway():
        return gamerocket.gamerocket_gateway.GamerocketGateway(Configuration.instantiate())
    
    @staticmethod
    def instantiate():
        return Configuration(
            Configuration.environment,
            Configuration.apiKey,
            Configuration.secretKey
        )
    
    @staticmethod
    def api_version():
        return "1"
    
    def __init__(self, environment, apiKey, secretKey):
        self.environment = environment
        self.apiKey = apiKey
        self.secretKey = secretKey
        self._http_strategy = self.__determine_http_strategy()
    
    def crypto(self):
        return gamerocket.util.crypto.Crypto(self)
    
    def http(self):
        return gamerocket.util.http.Http(self)
    
    def http_strategy(self):
        if Configuration.use_unsafe_ssl:
            return gamerocket.util.http_strategy.httplib_strategy.HttplibStrategy(self, self.environment)
        else:
            return self._http_strategy
    
    def __determine_http_strategy(self):
        return gamerocket.util.http_strategy.pycurl_strategy.PycurlStrategy(self, self.environment)
    
    def __http_strategy_from_environment(self):
	return gamerocket.util.http_strategy.pycurl_strategy.PycurlStrategy(self, self.environment)
        
    def sort_dict(self, dict):
        dict_sorted = OrderedDict(sorted(dict.items(), key=lambda t: t[0]))
        return dict_sorted
